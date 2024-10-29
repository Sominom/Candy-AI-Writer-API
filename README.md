## 엔드포인트

1. /complete
2. /enhance
3. /create
4. /is_subscribed
5. /get_domain_list
6. /get_credits
7. /admin/generate_api_key
8. /admin/extend_api_key
9. /admin/delete_api_key
10. /admin/set_max_domain_count
11. /admin/add_domain
12. /admin/delete_domain
13. /admin/set_subscribed

---

## 상세 설명

### 1. /complete

- 메소드: POST
- 설명: 주어진 프롬프트에 대한 완성 결과를 스트리밍으로 반환합니다.
- 요청 데이터: OpenAiRequestData
    - api_key (str): API 키
    - reference (str): 참조 문자열
    - prompt (str): 프롬프트 문자열
- 응답: 스트리밍 컨텐츠

### 2. /enhance

- 메소드: POST
- 설명: 주어진 프롬프트를 향상시킨 텍스트를 반환합니다.
- 요청 데이터: OpenAiRequestData
    - api_key (str): API 키
    - reference (str): 참조 문자열
    - prompt (str): 프롬프트 문자열
- 응답
    - message (str): 향상된 텍스트

### 3. /create

- 메소드: POST
- 설명: 주어진 프롬프트에 대해 HTML 형식의 결과를 생성합니다.
- 요청 데이터: OpenAiRequestData
    - api_key (str): API 키
    - reference (str): 참조 문자열
    - prompt (str): 프롬프트 문자열
- 응답
    - message (str): 생성된 HTML 문자열

### 4. /is_subscribed

- 메소드: GET
- 설명: API 키의 구독 상태를 확인합니다.
- 요청 데이터: RequestData
    - api_key (str): API 키
- 응답
    - message (str): 상태 메세지
    - subscribed (bool): 구독 상태

### 5. /get_domain_list

- 메소드: GET
- 설명: API 키에 연관된 도메인 리스트를 반환합니다.
- 요청 데이터: RequestData
    - api_key (str): API 키
- 응답
    - message (str): 상태 메세지
    - domain_list (list): 도메인 리스트

### 6. /get_credits

- 메소드: POST
- 설명: API 키에 남아있는 크레딧을 확인합니다.
- 요청 데이터: RequestData
    - api_key (str): API 키
- 응답
    - message (str): 상태 메세지
    - credits (int): 남은 크레딧

### 7. /admin/generate_api_key

- 메소드: POST
- 설명: 새로운 API 키를 생성합니다.
- 요청 데이터: GenerateApiKeyData
    - days (int): 유효 기간 (일)
    - secret (str): 관리자 비밀번호
- 응답
    - api_key (str): 생성된 API 키
    - expiration_date (str): 만료 날짜
    - message (str): 상태 메세지

### 8. /admin/extend_api_key

- 메소드: PUT
- 설명: 기존 API 키의 유효 기간을 연장합니다.
- 요청 데이터: ExtendApiKeyData
    - days (int): 연장할 기간 (일)
    - secret (str): 관리자 비밀번호
    - api_key (str): 연장할 API 키
- 응답
    - message (str): 상태 메세지

### 9. /admin/delete_api_key

- 메소드: DELETE
- 설명: 기존 API 키를 삭제합니다.
- 요청 데이터: DeleteApiKeyData
    - secret (str): 관리자 비밀번호
    - api_key (str): 삭제할 API 키
- 응답
    - message (str): 상태 메세지

### 10. /admin/set_max_domain_count

- 메소드: PUT
- 설명: 도메인 개수를 제한합니다.
- 요청 데이터: AdminRequestDataInt
    - api_key (str): 관리자 API 키
    - secret (str): 관리자 비밀번호
    - int (int): 최대 도메인 개수
- 응답
    - message (str): 상태 메세지

### 11. /admin/add_domain

- 메소드: PUT
- 설명: 도메인을 추가합니다.
- 요청 데이터: AdminRequestDataStr
    - api_key (str): 관리자 API 키
    - secret (str): 관리자 비밀번호
    - str (str): 추가할 도메인
- 응답
    - message (str): 상태 메세지

### 12. /admin/delete_domain

- 메소드: PUT
- 설명: 기존 도메인을 삭제합니다.
- 요청 데이터: AdminRequestDataStr
    - api_key (str): 관리자 API 키
    - secret (str): 관리자 비밀번호
    - str (str): 삭제할 도메인
- 응답
    - message (str): 상태 메세지

### 13. /admin/set_subscribed

- 메소드: PUT
- 설명: 구독 상태를 설정합니다.
- 요청 데이터: AdminRequestDataInt
    - api_key (str): 관리자 API 키
    - secret (str): 관리자 비밀번호
    - int (int): 구독 상태
- 응답
    - message (str): 상태 메세지
