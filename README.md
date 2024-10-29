# 설명
OpenAI API를 이용한 워드프레스의 Candy AI Writer 플러그인을 위한 API 서버입니다.
API 키별 크레딧 관리, 도메인 관리, 구독 상태 관리 등을 구현하였습니다.

크레딧이 부족하거나 구독이 만료되면 API 요청을 거부하며, 추후 관리 웹사이트를 통해 크레딧 충전, 도메인 추가, 구독 연장 등을 할 수 있게 구현할 예정이고, 유저가 결제를 통해 크레딧을 충전할 수 있도록 할 예정입니다.


# 설치 및 실행 가이드
### 설치
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x ./*.sh
deactivate
```

### 실행
```
./start.sh
```

### 종료
```
./stop.sh
```

### 로그 확인
```
tail -f server.log
```


# API 문서

### 1. 텍스트 완성 요청
- POST `/complete`
  - 설명: 주어진 프롬프트에 따라 텍스트를 완성합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 바디:
    - `prompt` (문자열) - (필수) 텍스트 생성에 사용할 프롬프트
    - `reference` (문자열) - (옵션) 참고할 추가 정보
  - 응답: 스트리밍된 텍스트 응답

### 2. 텍스트 개선 요청
- POST `/enhance`
  - 설명: 주어진 프롬프트를 개선하여 텍스트를 반환합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 바디:
    - `prompt` (문자열) - (필수) 개선할 프롬프트
  - 응답: 개선된 텍스트

### 3. HTML 생성 요청
- POST `/create`
  - 설명: 주어진 프롬프트로부터 HTML을 생성합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 바디:
    - `prompt` (문자열) - (필수) HTML 생성을 위한 프롬프트
  - 응답: 생성된 HTML

### 4. 구독 상태 확인
- GET `/is_subscribed`
  - 설명: 사용자의 구독 상태를 확인합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 응답: 구독 여부

### 5. 도메인 리스트 확인
- GET `/get_domain_list`
  - 설명: 사용자가 등록한 도메인 리스트를 반환합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 응답: 도메인 리스트

### 6. 크레딧 확인
- POST `/get_credits`
  - 설명: 사용 가능한 크레딧을 반환합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 응답: 사용 가능한 크레딧

### 7. API 키 만료 날짜 확인
- GET `/get_expiration_date`
  - 설명: API 키의 만료 날짜를 반환합니다.
  - 헤더: `api_key`: (필수) 사용자의 API 키
  - 응답: 만료 날짜

## 관리자 전용 엔드포인트

### 8. API 키 생성
- POST `/admin/generate_api_key`
  - 설명: 새로운 API 키를 생성합니다.
  - 헤더: `secret`: (필수) 관리자 비밀키
  - 쿼리: `days` (정수) - (필수) API 키의 유효 일수
  - 응답: 생성된 API 키

### 9. API 키 연장
- PUT `/admin/extend_api_key`
  - 설명: 기존 API 키의 만료 날짜를 연장합니다.
  - 헤더: `secret`: (필수) 관리자 비밀키
  - 쿼리:
    - `days` (정수) - (필수) 연장할 일수
    - `api_key` (문자열) - (필수) 연장할 API 키
  - 응답: 성공 메시지

### 10. API 키 삭제
- DELETE `/admin/delete_api_key`
  - 설명: API 키를 삭제합니다.
  - 헤더: `secret`: (필수) 관리자 비밀키
  - 쿼리: `api_key` (문자열) - (필수) 삭제할 API 키
  - 응답: 성공 메시지

### 11. 최대 도메인 개수 설정
- PUT `/admin/set_max_domain_count`
  - 설명: API 키에 대한 최대 도메인 개수를 설정합니다.
  - 헤더: `api_key`, `secret` (둘 다 필수) 사용자의 API 키 및 관리자 비밀키
  - 쿼리: `count` (정수) - (필수) 설정할 최대 도메인 개수
  - 응답: 성공 메시지

### 12. 도메인 추가
- PUT `/admin/add_domain`
  - 설명: 새로운 도메인을 추가합니다.
  - 헤더: `api_key`, `secret` (둘 다 필수) 사용자의 API 키 및 관리자 비밀키
  - 쿼리: `domain` (문자열) - (필수) 추가할 도메인명
  - 응답: 성공 메시지

### 13. 도메인 삭제
- PUT `/admin/delete_domain`
  - 설명: 등록된 도메인을 삭제합니다.
  - 헤더: `api_key`, `secret` (둘 다 필수) 사용자의 API 키 및 관리자 비밀키
  - 쿼리: `domain` (문자열) - (필수) 삭제할 도메인명
  - 응답: 성공 메시지

### 14. 구독 상태 설정
- PUT `/admin/set_subscribed`
  - 설명: 사용자의 구독 상태를 설정합니다.
  - 헤더: `api_key`, `secret` (둘 다 필수) 사용자의 API 키 및 관리자 비밀키
  - 쿼리: `subscribe_status` (정수) - (필수) 설정할 구독 상태
  - 응답: 성공 메시지
