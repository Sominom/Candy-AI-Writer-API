from datetime import datetime, timedelta
import string
import secrets
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from sqlalchemy.orm import Session # type: ignore
from contextlib import contextmanager
import pytz

from App.models.api_key import APIKey
from App.data.settings import Settings
from App.utils.conn import Base, Engine, SessionLocal

settings = Settings.get_instance()


class APIKeyService:

    @staticmethod
    def _validate_secret(secret: str) -> bool:
        return settings.secret == secret

    @staticmethod
    @contextmanager
    def _create_session():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _create_unique_api_key(session: Session) -> str:
        alphabet = string.ascii_letters + string.digits
        while True:
            api_key_str = settings.api_key_prefix + "".join(
                secrets.choice(alphabet) for _ in range(64)
            )
            if not session.query(APIKey).filter(APIKey.api_key == api_key_str).first():
                return api_key_str

    @staticmethod
    def generate_api_key(expiration_days: int, secret: str) -> str:
        Base.metadata.create_all(bind=Engine)

        if not APIKeyService._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with APIKeyService._create_session() as session:
            api_key = APIKeyService._create_unique_api_key(session)
            expiration_date = datetime.now(pytz.utc) + timedelta(days=expiration_days)
            api_key_obj = APIKey(api_key=api_key, expiration_date=expiration_date)
            session.add(api_key_obj)
            return api_key

    def _get_api_key(self, api_key: str, session: Session) -> APIKey:
        return session.query(APIKey).filter(APIKey.api_key == api_key).first()

    def authenticate_api_key(self, api_key: str) -> bool:
        with self._create_session() as session:
            return bool(self._get_api_key(api_key, session))

    def check_credits(self, api_key: str, credits: int = 1) -> bool:
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            return api_key_obj.credits >= credits if api_key_obj else False

    def modify_expiration(self, days: int, secret: str, api_key: str):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            api_key_obj.expiration_date += timedelta(days=days)

    def delete_api_key(self, secret: str, api_key: str):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            session.delete(api_key_obj)

    def get_credits(self, api_key: str) -> int:
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")
            return api_key_obj.credits

    def set_max_domain_count(self, api_key: str, secret: str, max_domain_count: int):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            api_key_obj.max_domain_count = max_domain_count

    def add_domain(self, api_key: str, secret: str, domain: str):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            domain_list = (
                api_key_obj.domain_list.split(",") if api_key_obj.domain_list else []
            )
            if len(domain_list) < api_key_obj.max_domain_count:
                domain_list.append(domain)
                api_key_obj.domain_list = ",".join(domain_list)
            else:
                raise ValueError("Maximum domain count exceeded")

    def delete_domain(self, api_key: str, secret: str, domain: str):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            domain_list = (
                api_key_obj.domain_list.split(",") if api_key_obj.domain_list else []
            )
            try:
                domain_list.remove(domain)
            except ValueError:
                raise ValueError("Domain not found")

            api_key_obj.domain_list = ",".join(domain_list)

    def get_domain_list(self, api_key: str) -> list:
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")
            return api_key_obj.domain_list.split(",") if api_key_obj.domain_list else []

    def is_subscribed(self, api_key: str) -> int:
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")
            return int(api_key_obj.is_subscribed)

    def set_subscribed(self, api_key: str, secret: str, is_subscribed: int):
        if not self._validate_secret(secret):
            raise ValueError("Unauthorized access")

        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            api_key_obj.is_subscribed = bool(is_subscribed)

    def increment_credits(self, api_key: str, credits: int):
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")
            api_key_obj.credits += credits
            return api_key_obj.credits

    def decrement_credits(self, api_key: str, credits: int):
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")

            if api_key_obj.credits < credits:
                api_key_obj.credits = 0
            else:
                api_key_obj.credits -= credits

    def get_expiration_date(self, api_key: str) -> datetime:
        with self._create_session() as session:
            api_key_obj = self._get_api_key(api_key, session)
            if not api_key_obj:
                raise ValueError("APIKey not found")
            return api_key_obj.expiration_date
