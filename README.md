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

### 초기 설정
```
settings-sample.json 파일을 settings.json으로 복사하고 데이터베이스, OpenAI API 키 설정 등을 수정하세요.
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
[API 문서](https://api.edix.studio/docs)를 참고하세요.