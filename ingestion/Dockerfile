# 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 1) 의존성 파일 복사 & 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) 소스코드 및 설정 파일 복사
COPY src/ ./src
COPY config/ingestion.yml ./config/ingestion.yml

# 3) 실행 시 .env 로드 및 파이프라인 실행
CMD ["python", "src/ingestion.py"]
