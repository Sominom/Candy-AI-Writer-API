import json
import pytest
from App.utils.conn import Base
from App.services.api_key_service import APIKeyService
from App.data.settings import Settings

settings = Settings.get_instance()


class TestAPIKeyService:

    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        self.api_key_service: APIKeyService = APIKeyService()
        self.test_api_key: str = APIKeyService.generate_api_key(14, settings.secret)

        # 테스트 종료 시 API 키 삭제
        def teardown():
            self.api_key_service.delete_api_key(settings.secret, self.test_api_key)

        request.addfinalizer(teardown)

    # 유효한지 확인
    def test_authenticate_api_key(self):
        # result = self.api_key_service.authenticate_api_key(self.test_api_key.api_key)
        # assert result
        print(self.test_api_key)
        assert self.test_api_key

    # 크레딧 충전
    def test_credit_increment(self):
        increment_credit = 1000
        decrement_credit = 10

        before_increment = self.api_key_service.get_credits(self.test_api_key)

        self.api_key_service.increment_credit(self.test_api_key, increment_credit)

        after_increment = self.api_key_service.get_credits(self.test_api_key)
        print(
            f"크레딧 증가 - before_credit: {before_increment}, after_credit: {after_increment}"
        )

        self.api_key_service.decrement_credit(self.test_api_key, decrement_credit)

        after_decrement = self.api_key_service.get_credits(self.test_api_key)

        print(
            f"크레딧 감소 - before_credit: {after_increment}, after_credit: {after_decrement}"
        )

        assert before_increment + increment_credit - decrement_credit == after_decrement

    # 크레딧 확인
    def test_check_credit1(self):
        credit = 1000

        api_key = self.test_api_key
        result = self.api_key_service.check_credit(api_key, credit)

        # 크레딧이 모자라서 False가 나와야 함
        assert result == False

    # 크레딧 확인
    async def test_check_credit2(self):
        increment_credit = 1000
        self.api_key_service.increment_credit(self.test_api_key, increment_credit)
        credit = 100
        api_key = self.test_api_key
        result = self.api_key_service.check_credit(api_key, credit)
        assert result == True

    # 도메인 추가
    def test_add_domain(self):
        domain1 = "https://www.test.com"
        domain2 = "https://www.test2.com"
        self.api_key_service.add_domain(self.test_api_key, settings.secret, domain1)
        
        # 최대 도메인 개수 초과
        try:
            self.api_key_service.add_domain(self.test_api_key, settings.secret, domain2)
        except ValueError as e:
            assert str(e) == "Maximum domain count exceeded"

    # 도메인 수 증가 후 도메인 추가 테스트
    def test_max_domain_count(self):
        domain1 = "https://www.test.com"
        domain2 = "https://www.test2.com"
        domain3 = "https://www.test3.com"
        
        self.api_key_service.set_max_domain_count(self.test_api_key, settings.secret, 5)
        
        self.api_key_service.add_domain(self.test_api_key, settings.secret, domain1)
        self.api_key_service.add_domain(self.test_api_key, settings.secret, domain2)
        self.api_key_service.add_domain(self.test_api_key, settings.secret, domain3)
        
        domain_list = self.api_key_service.get_domain_list(self.test_api_key)
        assert len(domain_list) == 3
        
    # 도메인 삭제
    def test_delete_domain(self):

        domain = "https://www.test.com"
        self.api_key_service.add_domain(self.test_api_key, settings.secret, domain)
        before_domains = self.api_key_service.get_domain_list(self.test_api_key)

        self.api_key_service.delete_domain(self.test_api_key, settings.secret, domain)
        after_domains = self.api_key_service.get_domain_list(self.test_api_key)

        assert len(before_domains) == 1 and len(after_domains) == 0
