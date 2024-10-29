from fastapi.responses import JSONResponse   # type: ignore
from sqlalchemy.orm import Session   # type: ignore
from App.models.api_key import APIKey
from datetime import datetime, timedelta  
import string  
import secrets  
import logging  
from App.data.settings import Settings  
from App.utils.conn import Base, Engine, SessionLocal  
from App.data.dtos import *  

settings = Settings.get_instance()  

class APIKeyService:  

    def __init__(self):  
        self.user_model = APIKey 

    async def _validate_secret(self, secret: str) -> bool:  
        return settings.secret == secret  

    def _response_error(self, message: str, e: Exception, session: Session) -> JSONResponse:  
        logging.error("%s: %s", message, str(e))  
        session.rollback()  
        return JSONResponse(content={"message": message}, status_code=500)  

    def _get_api_key(self, session: Session, api_key: str) -> APIKey:  
        return session.query(APIKey).filter(APIKey.api_key == api_key).first()  

    async def _modify_api_key(self, api_key: str, secret: str, modify_func, success_msg: str, error_msg: str) -> JSONResponse:  
        try:  
            if not await self._validate_secret(secret):  
                return JSONResponse(content={"message": "Unauthorized access"}, status_code=401)  

            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                if not user:  
                    return JSONResponse(content={"message": "APIKey not found"}, status_code=404)  
                try:  
                    modify_func(user)  
                    session.commit()  
                    return JSONResponse(content={"message": success_msg}, status_code=200)  
                except ValueError as ve:  
                    return JSONResponse(content={"message": str(ve)}, status_code=403)  
                except Exception as e:  
                    raise e  
        except Exception as e:  
            return self._response_error(error_msg, e, session)  

    async def authenticate_api_key(self, api_key) -> bool:  
        try:  
            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                return user and not user.is_expired()  
        except Exception as e:  
            logging.error("APIKey authentication failed: %s", str(e))  
            return False

    async def check_credit(self, api_key, credit: int = 1) -> bool:  
        try:  
            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                return user.credits >= credit if user else False  
        except Exception as e:  
            logging.error("Credit check failed: %s", str(e))  
            return False  

    async def authenticate_and_check_credit(self, api_key, credit: int = 1) -> bool:  
        return await self.authenticate_api_key(api_key) and await self.check_credit(api_key, credit)  

    async def generate_api_key(self, expiration_days: int, secret: str) -> JSONResponse:  
        try:  
            Base.metadata.create_all(bind=Engine)  

            if not await self._validate_secret(secret):  
                return JSONResponse(content={"message": "Unauthorized access"}, status_code=401)  

            alphabet = string.ascii_letters + string.digits  
            api_key = settings.api_key_prefix + ''.join(secrets.choice(alphabet) for _ in range(64))  

            with SessionLocal() as session:  
                if session.query(APIKey).filter(APIKey.api_key == api_key).first():  
                    return JSONResponse(content={"message": "API key already exists"}, status_code=409)  

                expiration_date = datetime.utcnow() + timedelta(days=expiration_days)  
                api_key_obj = APIKey(api_key=api_key, expiration_date=expiration_date)
                session.add(api_key_obj)  
                session.commit()  

                return JSONResponse(content={"api_key": api_key, "expiration_date": expiration_date.strftime("%Y-%m-%d"), "message": "API key generated successfully"}, status_code=200)  

        except Exception as e:  
            logging.error("API key generation failed: %s", str(e))  
            return JSONResponse(content={"message": "API key generation failed"}, status_code=500)  

    async def modify_expiration(self, days: int, secret: str, api_key: str) -> JSONResponse:  
        return await self._modify_api_key(  
            api_key, secret,  
            lambda user: setattr(user, 'expiration_date', user.expiration_date + timedelta(days=days)),  
            "API key extended successfully",  
            "API key extension failed"  
        )  

    async def delete_api_key(self, secret: str, api_key: str) -> JSONResponse:  
        return await self._modify_api_key(  
            api_key, secret,  
            lambda user: user.session.delete(user),  
            "API key deleted successfully",  
            "API key deletion failed"  
        )  

    async def adjust_credit(self, api_key: str, credit: int, increase: bool) -> JSONResponse:  
        return await self._modify_api_key(  
            api_key, None,   
            lambda user: user.credits + credit if increase else user.credits - credit,  
            "Credit adjusted successfully",  
            "Credit adjustment failed"  
        )  

    async def increase_credit(self, api_key: str, credit: int) -> JSONResponse:  
        return await self.adjust_credit(api_key, credit, increase=True)  

    async def decrease_credit(self, api_key: str, credit: int) -> JSONResponse:  
        return await self.adjust_credit(api_key, credit, increase=False)  

    async def get_credits(self, api_key: str) -> JSONResponse:  
        try:  
            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                if not user:  
                    return JSONResponse(content={"message": "APIKey not found"}, status_code=404)  
                return JSONResponse(content={"message": "Credit retrieved successfully", "credits": user.credits}, status_code=200)  
        except Exception as e:  
            return self._response_error("Credit retrieval failed", e, session)  

    async def set_max_domain_count(self, api_key: str, secret: str, max_domain_count: int) -> JSONResponse:  
        return await self._modify_api_key(  
            api_key, secret,  
            lambda user: setattr(user, 'max_domain_count', max_domain_count),  
            "Maximum domain count set successfully",  
            "Failed to set maximum domain count"  
        )  

    async def add_domain(self, api_key: str, secret: str, domain: str) -> JSONResponse:  
        def add_to_api_key_domains(user):  
            domain_list = user.domain_list.split(',')  
            if len(domain_list) < user.max_domain_count:  
                domain_list.append(domain)  
                user.domain_list = ','.join(domain_list)  
            else:  
                raise ValueError("Maximum domain count exceeded")  

        return await self._modify_api_key(  
            api_key, secret,  
            add_to_api_key_domains,  
            "Domain added successfully",  
            "Domain addition failed"  
        )  

    async def delete_domain(self, api_key: str, secret: str, domain: str) -> JSONResponse:  
        def remove_from_api_key_domains(user):  
            domain_list = user.domain_list.split(',')  
            domain_list.remove(domain)  
            user.domain_list = ','.join(domain_list)  

        return await self._modify_api_key(  
            api_key, secret,  
            remove_from_api_key_domains,  
            "Domain deleted successfully",  
            "Domain deletion failed"  
        )  

    async def get_domain_list(self, api_key: str) -> JSONResponse:  
        try:  
            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                if not user:  
                    return JSONResponse(content={"message": "APIKey not found"}, status_code=404)  
                domain_list = user.domain_list.split(',')  
                return JSONResponse(content={"message": "Domain list retrieved successfully", "domain_list": domain_list}, status_code=200)  
        except Exception as e:  
            return self._response_error("Failed to retrieve domain list", e, session)  

    async def is_subscribed(self, api_key: str) -> JSONResponse:  
        try:  
            with SessionLocal() as session:  
                user = self._get_api_key(session, api_key)  
                if not user:  
                    return JSONResponse(content={"message": "APIKey not found"}, status_code=404)  
                subscribed_status = 1 if user.is_subscribed else 0  
                return JSONResponse(content={"message": "Subscription status retrieved", "subscribed": subscribed_status}, status_code=200)  
        except Exception as e:  
            return self._response_error("Failed to check subscription status", e, session)  

    async def set_subscribed(self, api_key: str, secret: str, is_subscribed: int) -> JSONResponse:  
        return await self._modify_api_key(  
            api_key, secret,  
            lambda user: setattr(user, 'is_subscribed', bool(is_subscribed)),  
            "Subscription status updated successfully",  
            "Failed to update subscription status"  
        )