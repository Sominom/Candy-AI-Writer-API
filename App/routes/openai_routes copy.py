from App.utils.executor import Executor
from App.services.openai_service import complete, enhance, create
from App.services.user_service import decrease_credit, authenticate_user_and_check_credit
from App.data.dtos import OpenAiRequestData, RequestData

from fastapi.responses import JSONResponse, StreamingResponse # type: ignore
from fastapi import APIRouter # type: ignore
import traceback
import tiktoken # type: ignore


tokenizer = tiktoken.encoding_for_model('gpt-4o-mini')
executor = Executor.get_instance()
loop = Executor.get_loop()
router = APIRouter() 

@router.post("/complete")
async def complete_router(request: OpenAiRequestData):
    try:
        
        authData = RequestData(api_key=request.api_key, email=request.email)
        # API 키 인증
        if not await authenticate_user_and_check_credit(authData):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        async def generate_content_and_get_text():
            full_text = ""
            yield ""
            async for chunk in chat_stream(request):
                full_text += chunk
                yield chunk

            input_tokens = len(tokenizer.encode(request.prompt))
            output_tokens = len(tokenizer.encode(full_text))
            total_tokens = (input_tokens + output_tokens) / 10
            await decrease_credit(request.api_key, request.email, total_tokens)

        return StreamingResponse(generate_content_and_get_text(), media_type="text/plain")

    except Exception:
        traceback.print_exc()
        return JSONResponse(content={"message": "Internal server error"}, status_code=500)
    

@router.post("/organization")
async def enhance_router(request: OpenAiRequestData):
    try:
        authData = RequestData(api_key=request.api_key, email=request.email)
        # API 키 인증
        if not await authenticate_user_and_check_credit(authData):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        response = await enhance(request.prompt, request.reference)
        answer = response['answer']
        total_tokens = response['tokens'] / 10
        await decrease_credit(request.api_key, request.email, total_tokens)
        return JSONResponse(content={"message": "Organization successful", "response": answer}, status_code=200)
    except Exception:
        traceback.print_exc()
        return JSONResponse(content={"message": "Internal server error"}, status_code=500)

@router.post("/create")
async def create_router(request: OpenAiRequestData):
    try:
        authData = RequestData(api_key=request.api_key, email=request.email)
        # API 키 인증
        if not await authenticate_user_and_check_credit(authData):
            return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

        response = await create(request.prompt, request.reference)
        answer = response['answer']
        used_credit = response['tokens'] / 10
        await decrease_credit(request.api_key, request.email, used_credit)
        return JSONResponse(content={"message": "Created", "response": answer}, status_code=200)
    except Exception:
        traceback.print_exc()
        return JSONResponse(content={"message": "Internal server error"}, status_code=500)

    
    
async def chat_stream(prompt: str, reference: str = ""):
    full_text = await loop.run_in_executor(executor, complete, prompt, reference)
    async for chunk in full_text:
        yield chunk