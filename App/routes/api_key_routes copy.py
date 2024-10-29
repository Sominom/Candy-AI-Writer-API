from App.utils.executor import Executor
from App.data.dtos import RequestData, GenerateApiKeyData, ExtendApiKeyData, DeleteApiKeyData, AdminRequestDataInt, AdminRequestDataStr
from App.services.user_service import UserService
from fastapi import APIRouter # type: ignore

executor = Executor.get_instance()
router = APIRouter() 
user_service = UserService()

# 구독 여부 확인
@router.get("/is_subscribed")
async def is_subscribed(RequestData: RequestData):
    result = await user_service.is_subscribed(RequestData.api_key)
    return result

# 도메인 리스트
@router.get("/get_domain_list")
async def get_domain_list(RequestData: RequestData):
    result = await user_service.get_domain_list(RequestData.api_key)
    return result

# API 키 생성
@router.post("/admin/generate_user")
async def generate_user(GenerateApiKeyData: GenerateApiKeyData):
    return await user_service.generate_user(GenerateApiKeyData.days, GenerateApiKeyData.secret)

# API 키 연장
@router.put("/admin/extend_api_key")
async def extend_api_key(ExtendApiKeyData: ExtendApiKeyData):
    result = await user_service.extend_api_key(ExtendApiKeyData.days, ExtendApiKeyData.secret, ExtendApiKeyData.api_key)
    return result

# API 키 삭제
@router.delete("/admin/delete_user")
async def delete_user(DeleteApiKeyData: DeleteApiKeyData):
    result = await user_service.delete_user(DeleteApiKeyData.secret, DeleteApiKeyData.api_key)
    return result

# # 크레딧 증가
# @router.put("/admin/increase_credit")
# async def increase_credit(AdminRequestDataInt: AdminRequestDataInt):
#     result = await increase_credit(AdminRequestDataInt.api_key, AdminRequestDataInt.int)
#     return result

# 크레딧 확인
@router.post("/get_credits")
async def get_credits(RequestData: RequestData):
    result = await user_service.get_credits(RequestData.api_key)
    return result

# 도메인 개수 제한 설정
@router.put("/admin/set_max_domain_count")
async def set_max_domain_count(AdminRequestDataInt: AdminRequestDataInt):
    result = await user_service.set_max_domain_count(AdminRequestDataInt.api_key, AdminRequestDataInt.secret, AdminRequestDataInt.int)
    return result

# 도메인 추가
@router.put("/admin/add_domain")
async def add_domain(AdminRequestDataStr: AdminRequestDataStr):
    result = await user_service.add_domain(AdminRequestDataStr.api_key, AdminRequestDataStr.secret, AdminRequestDataStr.str)
    return result

# 도메인 삭제
@router.put("/admin/delete_domain")
async def delete_domain(AdminRequestDataStr: AdminRequestDataStr):
    result = await user_service.delete_domain(AdminRequestDataStr.api_key, AdminRequestDataStr.secret, AdminRequestDataStr.str)
    return result

# 구독 여부 설정
@router.put("/admin/set_subscribed")
async def set_subscribed(AdminRequestDataInt: AdminRequestDataInt):
    result = await user_service.set_subscribed(AdminRequestDataInt.api_key, AdminRequestDataInt.secret, AdminRequestDataInt.int)
    return result