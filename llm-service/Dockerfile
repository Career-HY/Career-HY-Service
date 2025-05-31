FROM python:3.12-slim

WORKDIR /app

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ .

# 포트 노출
EXPOSE 5003

# 애플리케이션 실행
CMD ["uvicorn", "llm_service:app", "--host", "0.0.0.0", "--port", "5003", "--reload"] 