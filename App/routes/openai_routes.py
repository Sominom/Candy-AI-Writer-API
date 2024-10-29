import token
import traceback
from typing import AsyncGenerator
from urllib import response
from uvicorn.config import logger as log
from fastapi.responses import JSONResponse, StreamingResponse  # type: ignore
from fastapi import HTTPException, APIRouter  # type: ignore
from App.services.api_key_service import APIKeyService
from App.services.openai_service import OpenAIService
from App.data.dtos import OpenAiRequestData, RequestData
from App.utils.executor import Executor
from App.data.settings import Settings

import tiktoken

settings = Settings.get_instance()
encoding = tiktoken.encoding_for_model(settings.openai_chat_model)


executor = Executor.get_instance()
router = APIRouter()

openai_service = OpenAIService()
api_key_service = APIKeyService()

def token_to_credit_calculater(prompt: str) -> int:
    token = len(encoding.encode(prompt))
    price = int(token / 10)
    
    return price
        
async def generator_wrapper(generator, input_message, api_key) -> AsyncGenerator[str, None]:
    output_message = ""
    async for message in generator:
        output_message += message
        yield message

    total_credits = token_to_credit_calculater(input_message + output_message)
    api_key_service.decrement_credit(api_key, total_credits)
    
@router.post("/complete")
async def complete_router(request: OpenAiRequestData):
    try:
        
        if not api_key_service.check_credit(request.api_key, token_to_credit_calculater(request.prompt)):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        complete_generator = openai_service.complete(request.prompt, request.reference)
        
        return StreamingResponse(
            content=generator_wrapper(complete_generator, request.prompt, request.api_key),
            media_type="text/plain"
        )

    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


@router.post("/enhance")
async def enhance_router(request: OpenAiRequestData):
    try:
        
        if not api_key_service.check_credit(request.api_key, token_to_credit_calculater(request.prompt)):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        enhance_str = await openai_service.enhance(request.prompt)
        
        total_token = token_to_credit_calculater(request.prompt + enhance_str)
        
        api_key_service.decrement_credit(request.api_key, total_token)

        return JSONResponse(content={"message": enhance_str}, status_code=200)

    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


@router.post("/create")
async def create_router(request: OpenAiRequestData):
    try:
        if not api_key_service.check_credit(request.api_key, token_to_credit_calculater(request.prompt)):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        html_str = await openai_service.create(request.prompt)
        
        total_token = token_to_credit_calculater(request.prompt + html_str)
        
        api_key_service.decrement_credit(request.api_key, total_token)

        return JSONResponse(content={"message": html_str}, status_code=200)

    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(content={"message": "Internal server error"}, status_code=500)
