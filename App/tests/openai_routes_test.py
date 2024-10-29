import json
from typing import AsyncGenerator
from fastapi.responses import JSONResponse, StreamingResponse
import pytest
from App.utils.conn import Base
from App.services.api_key_service import APIKeyService
from App.services.openai_service import OpenAIService
from App.data.settings import Settings
import requests
import tiktoken
settings = Settings.get_instance()

encoding = tiktoken.encoding_for_model(settings.openai_chat_model)

class TestOpenAIRoutes:

    def tokenizer(self, prompt: str) -> int:
        return len(encoding.encode(prompt))
    
    
    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        self.openai_service: OpenAIService = OpenAIService()
        self.api_key_service: APIKeyService = APIKeyService()
        self.test_api_key: str = APIKeyService.generate_api_key(14, settings.secret)
        
        # 크레딧 충전
        self.api_key_service.increment_credit(self.test_api_key, 3000)

        # 테스트 종료 시 API 키 삭제
        def teardown():
            self.api_key_service.delete_api_key(settings.secret, self.test_api_key)

        request.addfinalizer(teardown)
        
    def test_complete_router(self):
        
        input_prompt = "테스트"
        
        # 입력 토큰 계산
        input_token = self.tokenizer(input_prompt)
        
        data = {
            "api_key": self.test_api_key,
            "reference": "",
            "prompt": input_prompt
        }
        response = requests.post("http://localhost:8000/complete", json=data)
        
        full_text = ""
        
        if response.status_code == 200:
            for line in response.iter_lines():
                full_text += line.decode("utf-8")
                
        # 출력 토큰 계산
        output_token = self.tokenizer(full_text)
        
        # 10토큰당 1크레딧
        total_credits = 3000 - int((input_token + output_token) / 10)
        
        credits_data = {
            "api_key": self.test_api_key
        }
        
        credits_response = requests.post("http://localhost:8000/get_credits", json=credits_data)
        print(credits_response.json().get("credits"))
        
        my_credits = credits_response.json().get("credits")
        
        assert full_text
        
        # 크레딧 확인
        assert my_credits == total_credits
        

    def test_enhance_router(self):
        data = {
            "api_key": self.test_api_key,
            "reference": "",
            "prompt": "안영하세요 제 이르믄 정ㅈㅣㄴ 입니다"
        }
        
        response = requests.post("http://localhost:8000/enhance", json=data)
        
        print(response.json())
        assert response.status_code == 200
        assert response.json().get("message") == "안녕하세요. 제 이름은 정진입니다."
        
    def test_create_router(self):
        data = {
            "api_key": self.test_api_key,
            "reference": "",
            "prompt": "html 기본 템플릿 생성"
        }
        
        response = requests.post("http://localhost:8000/create", json=data)
        
        print(response.json())
        assert response.status_code == 200
        assert response.json().get("message")