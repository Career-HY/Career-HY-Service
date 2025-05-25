# 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 1) 의존성 파일 복사 & 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) 소스코드 및 설정 파일 복사
COPY src/ .

# 3) 포트 노출 및 실행
EXPOSE 5002
CMD ["uvicorn", "ingestion:app", "--host", "0.0.0.0", "--port", "5002", "--reload"]
