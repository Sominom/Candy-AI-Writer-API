from App.utils.openai_functions import openai_functions  
from App.utils.executor import Executor  
from App.data.settings import Settings
from App.data.prompts import *

import openai   # type: ignore
import traceback  
import re  
import asyncio  
import json  

executor = Executor.get_instance()  
loop = Executor.get_loop()

settings = Settings.get_instance()
openai_api_key = settings.openai_api_key

def clean_text(text: str) -> str:  
    text = text.replace("<br>", "\n")  
    text = text.replace("\n\n", "\n")  
    return text  

def clean_reference(reference: str) -> str:  
    reference = re.sub('<[^<]+?>', '', reference)  
    reference = reference.replace("\n\n", "\n")  
    return reference  

async def call_openai_api(  
    model: str,  
    prompts: list,  
    temperature: float,  
    max_tokens: int = 500,  
    stop: list = None,  
    function_call: dict = None  
) -> dict:  
    try:  
        response = await loop.run_in_executor(  
            executor,  
            lambda: openai.ChatCompletion.create(  
                model=model,  
                messages=prompts,  
                temperature=temperature,  
                max_tokens=max_tokens,  
                stop=stop,  
                functions=openai_functions if function_call else None,  
                function_call=function_call  
            )  
        )  
        return response  
    except Exception as e:  
        print("Error", e)
        traceback.print_exc()  
        return {}  

async def complete(prompt: str, reference: str = ""):  
    model = "gpt-3.5-turbo-0613"  
    temp = 0.6  

    prompt = clean_text(prompt)
    reference = clean_reference(reference)  

    prompts = []
    
    if reference:
        prompts = complete_prompt_with_reference()
    else:
        prompts = complete_prompt()


    response = await call_openai_api(model, prompts, temp, stream=True, stop=["."])  
    for chunk in response.get('choices', []):  
        chunk_message = chunk['delta'].get('content', '')  
        yield chunk_message  
    yield ". "  

async def enhance(prompt: str, reference: str = ""):  
    model = "gpt-3.5-turbo-16k-0613"  
    temp = 0.6  

    prompt = clean_text(prompt)  
    reference = clean_reference(reference)  
    
    prompts = []  
    if reference:  
        prompts = enhance_prompt_with_reference(reference, prompt)
    else:
        prompts = enhance_prompt(prompt) 
    
    response = await call_openai_api(model, prompts, temp, function_call={"name": "organization"})  
    tokens = response.get('usage', {}).get('total_tokens', 0)  
    answer = json.loads(response.get('choices', [{}])[0].get('message', {}).get("function_call", {}).get("arguments", "{}")).get("text", "")  
    return {"answer": answer, "tokens": tokens}  

async def create(prompt: str, reference: str = ""):  
    model = "gpt-3.5-turbo-0613"  
    temp = 0.6  

    prompt = clean_text(prompt)  
    reference = clean_reference(reference)  
    
    prompts = []
    
    if reference:
        prompts = create_prompt_with_reference(reference, prompt)
    else:
        prompts = create_prompt(prompt)

    response = await call_openai_api(model, prompts, temp, function_call={"name": "create_html"})  
    tokens = response.get('usage', {}).get('total_tokens', 0)  
    answer = json.loads(response.get('choices', [{}])[0].get('message', {}).get("function_call", {}).get("arguments", "{}")).get("html", "")  
    return {"answer": answer, "tokens": tokens}