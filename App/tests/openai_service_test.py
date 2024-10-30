import json
from typing import AsyncGenerator
import pytest # type: ignore
from App.utils.conn import Base
from App.services.api_key_service import APIKeyService
from App.services.openai_service import OpenAIService
from App.data.settings import Settings

settings = Settings.get_instance()


class TestOpenAIService:

    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        self.openai_service: OpenAIService = OpenAIService()
        self.api_key_service: APIKeyService = APIKeyService()
        self.test_api_key: str = APIKeyService.generate_api_key(14, settings.secret)
        
        # 크레딧 충전
        self.api_key_service.increment_credits(self.test_api_key, 3000)

        # 테스트 종료 시 API 키 삭제
        def teardown():
            self.api_key_service.delete_api_key(settings.secret, self.test_api_key)

        request.addfinalizer(teardown)

    # 프롬프트 테스트
    async def test_complete_chat(self):
        prompt = "수학문제를 푸시오. 테스트중이니 반드시 설명 없이 숫자만 답변 1024 + 6 = "
        result: AsyncGenerator = self.openai_service.complete(prompt)

        full_message = ""
        async for message in result:
            full_message += message
            print(message, end="", flush=True)
        
        assert full_message == "1030<END>"
        
    # 개선 테스트
    # async def test_enhance(self):
    #     prompt = "안영하세요 제 이르믄 정ㅈㅣㄴ 입니다"
    #     result = await self.openai_service.enhance(prompt)
    #     print(result)
    #     assert result == "안녕하세요. 제 이름은 정진입니다."

    # # 생성 테스트
    # async def test_create(self):
    #     prompt = "html 기본 템플릿 생성"
    #     result = await self.openai_service.create(prompt)
    #     print(result)
    #     assert result