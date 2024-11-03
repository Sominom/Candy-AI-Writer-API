from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, APIRouter, Request, Header
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import tiktoken
import traceback
from uvicorn.config import logger as log

from App.services.api_key_service import APIKeyService
from App.services.openai_service import OpenAIService
from App.data.settings import Settings

settings = Settings.get_instance()
encoding = tiktoken.encoding_for_model(settings.openai_chat_model)

app = FastAPI()
router = APIRouter()

openai_service = OpenAIService()
api_key_service = APIKeyService()


class OpenAIRequestDTO(BaseModel):
    prompt: str
    reference: str


def token_to_credits_calculater(prompt: str) -> int:
    token = len(encoding.encode(prompt))
    price = int(token / 10)
    return price


async def generator_wrapper(
    generator, input_message, api_key
) -> AsyncGenerator[str, None]:
    output_message = ""
    async for message in generator:
        output_message += message
        yield message
    total_credits = token_to_credits_calculater(input_message + output_message)
    api_key_service.decrement_credits(api_key, total_credits)


@router.post("/complete", response_class=StreamingResponse)
async def complete_router(
    body: OpenAIRequestDTO,
    api_key: str = Header(..., alias="X-API-Key"),
):
    """
    글을 완성시킵니다.
    """
    try:
        if not api_key_service.check_credits(
            api_key, token_to_credits_calculater(body.prompt)
        ):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        complete_generator = openai_service.complete(body.prompt, body.reference)
        return StreamingResponse(
            content=generator_wrapper(complete_generator, body.prompt, api_key),
            media_type="text/plain",
        )
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


@router.post("/enhance")
async def enhance_router(
    body: OpenAIRequestDTO,
    api_key: str = Header(..., alias="X-API-Key"),
):
    """
    글의 문법이나 표현 등을 개선합니다.
    """
    try:
        if not api_key_service.check_credits(
            api_key, token_to_credits_calculater(body.prompt)
        ):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        enhance_str = await openai_service.enhance(body.prompt, body.reference)
        total_token = token_to_credits_calculater(body.prompt + enhance_str)
        api_key_service.decrement_credits(api_key, total_token)
        return JSONResponse(content={"message": enhance_str}, status_code=200)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


@router.post("/create", response_model=OpenAIRequestDTO)
async def create_router(
    body: OpenAIRequestDTO,
    api_key: str = Header(..., alias="X-API-Key"),
):
    """
    HTML을 생성합니다.
    """
    try:
        if not api_key_service.check_credits(
            api_key, token_to_credits_calculater(body.prompt)
        ):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        html_str = await openai_service.create(body.prompt, body.reference)
        total_token = token_to_credits_calculater(body.prompt + html_str)
        api_key_service.decrement_credits(api_key, total_token)
        return JSONResponse(content={"message": html_str}, status_code=200)
    except Exception:
        log.error(traceback.format_exc())
        return JSONResponse(
            content={"message": "Internal server error"}, status_code=500
        )


app.include_router(router)
