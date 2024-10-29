import traceback  
import logging  
from App.utils.executor import Executor  
from App.data.dtos import (  
    RequestData,  
    GenerateApiKeyData,  
    ExtendApiKeyData,  
    DeleteApiKeyData,  
    AdminRequestDataInt,  
    AdminRequestDataStr,  
)  
from App.services.api_key_service import APIKeyService  
from fastapi import APIRouter, HTTPException  
from fastapi.responses import JSONResponse  

executor = Executor.get_instance()  
router = APIRouter()  
api_key_service = APIKeyService()  
log = logging.getLogger(__name__)  

# 구독 여부 확인  
@router.get("/is_subscribed")  
async def is_subscribed(request_data: RequestData):  
    try:  
        result = api_key_service.is_subscribed(request_data.api_key)  
        return JSONResponse(  
            content={"message": "Subscription status retrieved", "subscribed": result}  
        )  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 도메인 리스트  
@router.get("/get_domain_list")  
async def get_domain_list(request_data: RequestData):  
    try:  
        result = api_key_service.get_domain_list(request_data.api_key)  
        return JSONResponse(  
            content={"message": "Domain list retrieved successfully", "domain_list": result}  
        )  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 크레딧 확인  
@router.post("/get_credits")  
async def get_credits(request_data: RequestData):  
    try:  
        credits = api_key_service.get_credits(request_data.api_key)  
        return JSONResponse(  
            content={"message": "Credit retrieved successfully", "credits": credits}  
        )  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# API 키 생성  
@router.post("/admin/generate_api_key")  
async def generate_api_key(generate_api_key_data: GenerateApiKeyData):  
    try:  
        api_key_obj = api_key_service.generate_api_key(  
            generate_api_key_data.days, generate_api_key_data.secret  
        )  
        return JSONResponse(  
            content={  
                "api_key": api_key_obj.get_api_key(),  
                "expiration_date": api_key_obj.get_expiration_date(),  
                "message": "API key generated successfully",  
            }  
        )  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# API 키 연장  
@router.put("/admin/extend_api_key")  
async def extend_api_key(extend_api_key_data: ExtendApiKeyData):  
    try:  
        api_key_service.modify_expiration(  
            extend_api_key_data.days,  
            extend_api_key_data.secret,  
            extend_api_key_data.api_key,  
        )  
        return JSONResponse(content={"message": "API key extended successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# API 키 삭제  
@router.delete("/admin/delete_api_key")  
async def delete_user(delete_api_key_data: DeleteApiKeyData):  
    try:  
        api_key_service.delete_api_key(  
            delete_api_key_data.secret, delete_api_key_data.api_key  
        )  
        return JSONResponse(content={"message": "API key deleted successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 도메인 개수 제한 설정  
@router.put("/admin/set_max_domain_count")  
async def set_max_domain_count(admin_request_data_int: AdminRequestDataInt):  
    try:  
        api_key_service.set_max_domain_count(  
            admin_request_data_int.api_key,  
            admin_request_data_int.secret,  
            admin_request_data_int.int,  
        )  
        return JSONResponse(content={"message": "Maximum domain count set successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 도메인 추가  
@router.put("/admin/add_domain")  
async def add_domain(admin_request_data_str: AdminRequestDataStr):  
    try:  
        api_key_service.add_domain(  
            admin_request_data_str.api_key,  
            admin_request_data_str.secret,  
            admin_request_data_str.str,  
        )  
        return JSONResponse(content={"message": "Domain added successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 도메인 삭제  
@router.put("/admin/delete_domain")  
async def delete_domain(admin_request_data_str: AdminRequestDataStr):  
    try:  
        api_key_service.delete_domain(  
            admin_request_data_str.api_key,  
            admin_request_data_str.secret,  
            admin_request_data_str.str,  
        )  
        return JSONResponse(content={"message": "Domain deleted successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )  

# 구독 여부 설정  
@router.put("/admin/set_subscribed")  
async def set_subscribed(admin_request_data_int: AdminRequestDataInt):  
    try:  
        api_key_service.set_subscribed(  
            admin_request_data_int.api_key,  
            admin_request_data_int.secret,  
            admin_request_data_int.int,  
        )  
        return JSONResponse(content={"message": "Subscription status updated successfully"})  
    except Exception:  
        log.error(traceback.format_exc())  
        return JSONResponse(  
            content={"message": "Internal server error"}, status_code=500  
        )