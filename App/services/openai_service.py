from turtle import st
from typing import AsyncGenerator
from App.utils.openai_functions import openai_functions
from App.utils.executor import Executor
from App.data.settings import Settings
from App.data.prompts import *
from openai import AsyncOpenAI # type: ignore
import traceback
import re
import asyncio
import json

executor = Executor.get_instance()
settings = Settings.get_instance()

end_flag = "<END>"
error_flag = "<ERROR>"

class OpenAIService:
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    def clean_text(self, text: str) -> str:
        text = text.replace("<br>", "\n")
        text = text.replace("\n\n", "\n")
        return text

    def clean_reference(self, reference: str) -> str:
        reference = re.sub("<[^<]+?>", "", reference)
        reference = reference.replace("\n\n", "\n")
        return reference

    async def call_openai_api(
        self,
        prompts: list[dict],
        function_call: dict = None,
    ):
        model = settings.openai_chat_model
        temperature = 0.6
        max_tokens = 500
        # stop = [". "]
        
        is_function = False
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=prompts,
                temperature=temperature,
                max_tokens=max_tokens,
                # stop=stop,
                functions=openai_functions if function_call else None,
                function_call=function_call,
                stream=True,
            )
            async for chunk in response:
                choice = chunk.choices[0]
                message = chunk.choices[0].delta.content
                
                if message:
                    yield message
                    
                if choice.delta.function_call:
                    is_function = True
                    yield choice.delta.function_call.arguments
                    
            if not is_function:
                yield end_flag
        except Exception as e:
            yield error_flag

    async def complete(self, prompt: str, reference: str = "") -> AsyncGenerator[str, None]:
        prompt = self.clean_text(prompt)
        reference = self.clean_reference(reference)
        
        prompts = []
        
        if reference:
            prompts = complete_prompt_with_reference(prompt, reference)
        else:
            prompts = complete_prompt(prompt)

        response = self.call_openai_api(prompts)
        async for message in response:
            yield message

    async def enhance(self, prompt: str, reference: str = "") -> str:
        prompt = self.clean_text(prompt)
        reference = self.clean_reference(reference)

        prompts = []
        
        if reference:
            prompts = enhance_prompt_with_reference(reference, prompt)
        else:
            prompts = enhance_prompt(prompt)

        response = self.call_openai_api(prompts, function_call={"name": "organization"})
        
        full_message = ""
        async for chunk in response:
            full_message += chunk
        
        message = json.loads(full_message).get("text")
        return message
            

    async def create(self, prompt: str, reference: str = "") -> str:
        prompt = self.clean_text(prompt)
        reference = self.clean_reference(reference)

        prompts = []
        
        if reference:
            prompts = enhance_prompt_with_reference(reference, prompt)
        else:
            prompts = enhance_prompt(prompt)

        response = self.call_openai_api(prompts, function_call={"name": "create_html"})
        
        full_message = ""
        async for chunk in response:
            full_message += chunk
            
        message = json.loads(full_message).get("html")
        return message
