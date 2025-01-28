## GREPP 과제
언어 및 프레임워크: python & FastAPI
## 실행 방법
### git clone
```commandline
git clone https://github.com/cheon4050/grepp-be.git
```
### DB 실행환경
postgresql 도커 컨테이너 실행 커맨드
```commandline
docker-compose up -d
```
### 파이썬 실행 환경
파이썬 버전: 3.12 <br>
환경 설정 커맨드 
```commandline
pip install -r requirements.txt
```

### 앱 실행
```commandline
uvicorn main:app
```

## API 문서
fastapi의 swagger를 활용해서 작성했습니다. 앱 실행 후 조회 가능합니다.
```commandline
http://localhost:8000/docs
```

