FROM python:3.11-slim
WORKDIR /app

# 0) 시스템 빌드 도구 & CMake 설치
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
 && rm -rf /var/lib/apt/lists/*

# 1) requirements 복사
COPY requirements.txt ./

# 2) pip·setuptools·wheel 업그레이드
RUN pip install --upgrade pip setuptools wheel

# 3) numpy 먼저 설치 (kiwipiepy 빌드시 import 오류 방지)
RUN pip install --no-cache-dir numpy

# 4) 나머지 패키지 설치 (빌드 격리 해제)
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# 5) 소스 복사
COPY src/ .

# 6) 실행
EXPOSE 5002
CMD ["uvicorn", "ingestion:app", "--host", "0.0.0.0", "--port", "5002", "--reload"]
