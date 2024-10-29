from fastapi.responses import JSONResponse  
from sqlalchemy.orm import Session  
from models import User  
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import Column, String, Integer, Date, Boolean
import string
import secrets
import traceback
import requests
import random
import logging
from data import admin_pass
from conn import Base, Engine, SessionLocal

#크레딧이 충분한지 확인하는 함수
async def checkCredit(api_key: str, email: str, credit: int) -> bool:
    try:
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return False
            if api_key_obj.credits < credit:
                return False
            return True
    except Exception as e:
        logging.error("Credit check failed: %s", str(e))
        return False

# API 키 검증 함수
async def authenticateUser(api_key: str, email: str) -> bool:
    try:
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj or api_key_obj.is_expired():
                return False
            return api_key_obj
    except Exception as e:
        logging.error("API key authentication failed: %s", str(e))
        return False

# 관리자 암호 검증 함수
async def authenticateAdminPassword(admin_password: str) -> bool:
    if admin_password != admin_pass:
        return False
    return True

# API 키 생성 함수
async def generateUser(expiration_days: int, email: str, admin_password: str) -> JSONResponse:
    try:
        #테이블이 없으면 생성
        Base.metadata.create_all(bind=Engine)
        
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        # API 키 생성
        alphabet = string.ascii_letters + string.digits
        with SessionLocal() as session:
            api_key=""
            while True:
                api_key = 'cb_' + ''.join(secrets.choice(alphabet) for _ in range(64))
                existing_key = session.query(User).filter(User.api_key == api_key, User.email == email).first()
                if not existing_key:
                    break
            
            # 생성된 API 키를 저장
            api_key_obj = User(id=api_key)
            api_key_obj.set_expiration_date(days=expiration_days)
            api_key_obj.set_email(email)
            session.add(api_key_obj)
            session.commit()

            # Session을 사용하여 expiration_date 값을 가져옵니다.
            expiration_date = session.query(User).filter(User.api_key == api_key, User.email == email).first().expiration_date
            content = {
                "api_key": api_key,
                "expiration_date": expiration_date.strftime("%Y-%m-%d"),
                "message": "API key generated successfully",
            }
            return JSONResponse(content=content, status_code=200)
    except Exception as e:
        logging.error("API key generation failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "API key generation failed"}, status_code=500)

# API 키 연장 함수
async def extendUser(days: int, email: str, admin_password: str, api_key: str) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # API 키의 유효 기간 연장
            new_expiration_date = api_key_obj.expiration_date + timedelta(days=days)
            api_key_obj.set_expiration_date(new_expiration_date)
            session.commit()
            return JSONResponse(content={"message": "API key extended successfully","expiration_date": api_key_obj.expiration_date}, status_code=200)
    except Exception as e:
        logging.error("API key extension failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "API key extension failed",}, status_code=500)

# API 키 삭제 함수
async def deleteUser(admin_password: str, email: str, api_key: str) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # API 키 삭제
            session.delete(api_key_obj)
            session.commit()
            return JSONResponse(content={"message": "API key deleted successfully"}, status_code=200)
    except Exception as e:
        logging.error("API key deletion failed: %s", str(e))
        session.rollback()  # rollback the session in case of failure
        return JSONResponse(content={"message": "API key deletion failed", "status_code": 500}, status_code=500)

    
# 크레딧 감소 함수
async def decreaseCredit(api_key: str, email: str, admin_password: str, credit: int) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # 크레딧 감소
            api_key_obj.subtract_credit(credit)
            session.commit()
            final_credits = api_key_obj.get_credit()

            return JSONResponse(content={"message": "Credit decreased successfully", "credits": final_credits}, status_code=200)
    except Exception as e:
        logging.error("Credit decrease failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Credit decrease failed"}, status_code=500)

# 크레딧 증가 함수
async def increaseCredit(api_key: str, email: str, admin_password: str, credit: int) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # 크레딧 증가
            api_key_obj.add_credit(credit)
            session.commit()
            final_credits = api_key_obj.get_credit()

            return JSONResponse(content={"message": "Credit increased successfully", "credits": final_credits}, status_code=200)
    except Exception as e:
        logging.error("Credit increase failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Credit increase failed"}, status_code=500)

# 크레딧 조회 함수
async def getCredits(api_key: str, email: str) -> JSONResponse:
    try:
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if api_key_obj:
                return JSONResponse(content={"message": "Credit retrieved successfully", "credits": api_key_obj.credits}, status_code=200)
            else:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)
    except Exception as e:
        logging.error("Credit retrieval failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Credit retrieval failed"}, status_code=500)
    
# 도메인 갯수 제한 설정 함수
async def setMaxDomainCount(api_key: str, email: str, admin_password: str, max_domain_count: int) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # 도메인 갯수 제한 설정
            api_key_obj.max_domain_count = max_domain_count
            session.commit()
            return JSONResponse(content={"message": "Maximum domain count set successfully"}, status_code=200)
    except Exception as e:
        logging.error("Maximum domain count setting failed: %s", str(e))
        traceback.print_exc()
        return JSONResponse(content={"message": "Maximum domain count setting failed"}, status_code=500)


# 도메인 추가 함수
async def addDomain(api_key: str, email: str, admin_password: str, domain: str) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # max_domain_count와 domain_list를 비교해서 max_domain_count보다 작으면 도메인 추가
            domain_list = api_key_obj.domain_list.split(',')
            if len(domain_list) < api_key_obj.max_domain_count:
                domain_list.append(domain)
                api_key_obj.domain_list = ','.join(domain_list)
                session.commit()
                return JSONResponse(content={"message": "Domain added successfully"}, status_code=200)
            else:
                return JSONResponse(content={"message": "Maximum domain count exceeded"}, status_code=403)
    except Exception as e:
        logging.error("Domain addition failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Domain addition failed"}, status_code=500)
    
# 도메인 삭제 함수
async def deleteDomain(api_key: str, email: str, admin_password: str, domain: str) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)
            
            # 도메인 삭제
            domain_list = api_key_obj.domain_list.split(',')
            domain_list.remove(domain)
            api_key_obj.domain_list = ','.join(domain_list)
            session.commit()
            return JSONResponse(content={"message": "Domain deleted successfully"}, status_code=200)
    except Exception as e:
        logging.error("Domain deletion failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Domain deletion failed"}, status_code=500)
    
# 도메인을 리스트로 가져오기 함수
async def getDomainList(api_key: str, email: str) -> JSONResponse:
    try:
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # 도메인 리스트 가져오기
            domain_list = api_key_obj.domain_list.split(',')
            return JSONResponse(content={"message": "Domain list retrieved successfully", "domain_list": domain_list}, status_code=200)
    except Exception as e:
        logging.error("Domain list retrieval failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Domain list retrieval failed"}, status_code=500)
    
#구독 여부 확인 함수
async def isSubscribed(api_key: str, email: str) -> JSONResponse:
    try:
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            if api_key_obj.is_subscribed:
                return JSONResponse(content={"message": "Subscription status retrieved successfully", "subscribed": 1}, status_code=200)
            else:
                return JSONResponse(content={"message": "Subscription status retrieved successfully", "subscribed": 0}, status_code=200)
    except Exception as e:
        logging.error("Subscription status check failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Subscription status check failed"}, status_code=500)
    
#구독 여부 설정 함수
async def setSubscribed(api_key: str, email: str, admin_password: str, is_subscribed: int) -> JSONResponse:
    try:
        if not await authenticateAdminPassword(admin_password):
            return JSONResponse(content={"message": "Unable to access"}, status_code=401)
        with SessionLocal() as session:
            api_key_obj = session.query(User).filter(User.api_key == api_key, User.email == email).first()
            if not api_key_obj:
                return JSONResponse(content={"message": "API key not found"}, status_code=404)

            # 구독 여부 설정
            api_key_obj.is_subscribed = is_subscribed
            session.commit()
            return JSONResponse(content={"message": "Subscription status set successfully", "subscribed": is_subscribed}, status_code=200)
    except Exception as e:
        logging.error("Subscription status setting failed: %s", str(e))
        session.rollback()
        return JSONResponse(content={"message": "Subscription status setting failed"}, status_code=500)
    