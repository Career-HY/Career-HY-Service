FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치 (Chromium + ChromeDriver)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver \
    # Chromium 의존성
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libgbm1 \
    # 추가 유틸리티
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 기본 명령어 (docker-compose에서 override 가능)
CMD ["python", "scheduler.py"]
