from multiprocessing import Value
import traceback
import logging
from typing import Dict
from wsgiref import headers
from fastapi import APIRouter, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from App.services.api_key_service import APIKeyService
from App.data.dtos import *

router = APIRouter()
api_key_service = APIKeyService()
log = logging.getLogger(__name__)


# 구독 여부 확인
@router.get("/is_subscribed", response_model=APISubscriptionResponse)
async def is_subscribed(api_key: str = Header(..., alias="X-API-Key")):
    """
    API 키의 구독 여부를 확인합니다.
    """
    try:
        result = api_key_service.is_subscribed(api_key)
        return {"message": "Subscription status retrieved", "subscribed": result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 도메인 리스트
@router.get("/get_domain_list", response_model=DomainListResponse)
async def get_domain_list(api_key: str = Header(..., alias="X-API-Key")):
    """
    API 키의 도메인 리스트를 확인합니다.
    """
    try:
        result = api_key_service.get_domain_list(api_key)
        return {"message": "Domain list retrieved successfully", "domain_list": result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 크레딧 확인
@router.get("/get_credits", response_model=CreditsResponse)
async def get_credits(api_key: str = Header(..., alias="X-API-Key")):
    """
    API 키의 크레딧을 확인합니다.
    """
    try:
        credits = api_key_service.get_credits(api_key)
        return {"message": "Credits retrieved successfully", "credits": credits}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 만료날짜 확인
@router.get("/get_expiration_date", response_model=ExpirationDateResponse)
async def get_expiration_date(api_key: str = Header(..., alias="X-API-Key")):
    """
    API 키의 만료날짜를 확인합니다.
    """
    try:
        expiration_date = api_key_service.get_expiration_date(api_key)
        return {
            "message": "Expiration date retrieved successfully",
            "expiration_date": str(expiration_date),
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# API 키 생성
@router.post("/admin/generate_api_key", response_model=ApiKeyResponse)
async def generate_api_key(body: DaysDTO, secret: str = Header(None, alias="X-Secret")):
    """
    API 키를 생성합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key = api_key_service.generate_api_key(body.days, secret)
        return {"api_key": api_key, "message": "API key generated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# API 키 연장
@router.put("/admin/extend_api_key", response_model=SuccessMessageResponse)
async def extend_api_key(
    body: DaysDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키의 만료일을 연장합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.modify_expiration(body.days, secret, api_key)
        return {"message": "API key extended successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# API 키 삭제
@router.delete("/admin/delete_api_key", response_model=SuccessMessageResponse)
async def delete_user(
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키를 삭제합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.delete_api_key(secret, api_key)
        return {"message": "API key deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 도메인 개수 제한 설정
@router.put("/admin/set_max_domain_count", response_model=SuccessMessageResponse)
async def set_max_domain_count(
    body: DomainCountDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키의 도메인 개수 제한을 설정합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.set_max_domain_count(api_key, secret, body.count)
        return {"message": "Maximum domain count set successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 도메인 추가
@router.put("/admin/add_domain", response_model=SuccessMessageResponse)
async def add_domain(
    body: DomainDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키에 도메인을 추가합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.add_domain(api_key, secret, body.domain)
        return {"message": "Domain added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 도메인 삭제
@router.put("/admin/delete_domain", response_model=SuccessMessageResponse)
async def delete_domain(
    body: DomainDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키에서 도메인을 삭제합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.delete_domain(api_key, secret, body.domain)
        return {"message": "Domain deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 구독 여부 설정
@router.put("/admin/set_subscribed", response_model=SuccessMessageResponse)
async def set_subscribed(
    body: StatusDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키의 구독 여부를 설정합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.set_subscribed(api_key, secret, body.status)
        return {"message": "Subscription status updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# 크레딧 증가
@router.put("/admin/increment_credits", response_model=SuccessMessageResponse)
async def increment_credits(
    body: CreditsDTO,
    api_key: str = Header(..., alias="X-API-Key"),
    secret: str = Header(None, alias="X-Secret"),
):
    """
    API 키의 크레딧을 증가합니다.
    """
    try:
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.increment_credits(api_key, body.credits)
        return {"message": "Credits incremented successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=e.args[0])
    except Exception:
        log.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
