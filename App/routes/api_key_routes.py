from multiprocessing import Value
import traceback
import logging
from App.services.api_key_service import APIKeyService
from App.data.dtos import DaysDTO, DomainCountDTO, DomainDTO, StatusDTO, CreditsDTO
from fastapi import APIRouter, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore

router = APIRouter()
api_key_service = APIKeyService()
log = logging.getLogger(__name__)


# 구독 여부 확인
@router.get("/is_subscribed")
async def is_subscribed(request: Request):
    try:
        api_key = request.headers.get("api_key")
        if not api_key:
            raise ValueError("API key is missing in headers")
        result = api_key_service.is_subscribed(api_key)
        return JSONResponse(
            content={"message": "Subscription status retrieved", "subscribed": result}
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 도메인 리스트
@router.get("/get_domain_list")
async def get_domain_list(request: Request):
    try:
        api_key = request.headers.get("api_key")
        if not api_key:
            raise ValueError("API key is missing in headers")
        result = api_key_service.get_domain_list(api_key)
        return JSONResponse(
            content={
                "message": "Domain list retrieved successfully",
                "domain_list": result,
            }
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 크레딧 확인
@router.get("/get_credits")
async def get_credits(request: Request):
    try:
        api_key = request.headers.get("api_key")
        if not api_key:
            raise ValueError("API key is missing in headers")
        credits = api_key_service.get_credits(api_key)
        return JSONResponse(
            content={"message": "Credits retrieved successfully", "credits": credits}
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 만료날짜 확인
@router.get("/get_expiration_date")
async def get_expiration_date(request: Request):
    try:
        api_key = request.headers.get("api_key")
        if not api_key:
            raise ValueError("API key is missing in headers")
        expiration_date = api_key_service.get_expiration_date(api_key)
        return JSONResponse(
            content={
                "message": "Expiration date retrieved successfully",
                "expiration_date": str(expiration_date),
            }
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# API 키 생성
@router.post("/admin/generate_api_key")
async def generate_api_key(request: Request, body: DaysDTO):
    try:
        secret = request.headers.get("secret")
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key = api_key_service.generate_api_key(body.days, secret)
        return JSONResponse(
            content={"api_key": api_key, "message": "API key generated successfully"}
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# API 키 연장
@router.put("/admin/extend_api_key")
async def extend_api_key(request: Request, body: DaysDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.modify_expiration(body.days, secret, api_key)
        return JSONResponse(content={"message": "API key extended successfully"})
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# API 키 삭제
@router.delete("/admin/delete_api_key")
async def delete_user(request: Request):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not secret:
            raise ValueError("Secret is missing in headers")
        api_key_service.delete_api_key(secret, api_key)
        return JSONResponse(content={"message": "API key deleted successfully"})
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 도메인 개수 제한 설정
@router.put("/admin/set_max_domain_count")
async def set_max_domain_count(request: Request, body: DomainCountDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not api_key or not secret:
            raise ValueError("API key or secret is missing in headers")
        api_key_service.set_max_domain_count(api_key, secret, body.count)
        return JSONResponse(
            content={"message": "Maximum domain count set successfully"}
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 도메인 추가
@router.put("/admin/add_domain")
async def add_domain(request: Request, body: DomainDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not api_key or not secret:
            raise ValueError("API key or secret is missing in headers")
        api_key_service.add_domain(api_key, secret, body.domain)
        return JSONResponse(content={"message": "Domain added successfully"})
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 도메인 삭제
@router.put("/admin/delete_domain")
async def delete_domain(request: Request, body: DomainDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not api_key or not secret:
            raise ValueError("API key or secret is missing in headers")
        api_key_service.delete_domain(api_key, secret, body.domain)
        return JSONResponse(content={"message": "Domain deleted successfully"})
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 구독 여부 설정
@router.put("/admin/set_subscribed")
async def set_subscribed(request: Request, body: StatusDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not api_key or not secret:
            raise ValueError("API key or secret is missing in headers")
        api_key_service.set_subscribed(api_key, secret, body.status)
        return JSONResponse(
            content={"message": "Subscription status updated successfully"}
        )
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


# 크레딧 증가
@router.put("/admin/increment_credits")
async def increment_credits(request: Request, body: CreditsDTO):
    try:
        api_key = request.headers.get("api_key")
        secret = request.headers.get("secret")
        if not api_key or not secret:
            raise ValueError("API key or secret is missing in headers")
        api_key_service.increment_credits(api_key, body.credits)
        return JSONResponse(content={"message": "Credits incremented successfully"})
    except ValueError as e:
        return JSONResponse(content={"message": e.args[0]}, status_code=401)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )
