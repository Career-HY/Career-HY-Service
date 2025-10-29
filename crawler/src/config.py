"""
환경변수 및 설정 관리
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 로드
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# AWS 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "career-hi")

# 크롤링 설정
CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "50"))
CRAWL_MODE = os.getenv("CRAWL_MODE", "daily")  # 'test', 'daily', 'initial'

# Ingestion API 설정
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:5002")

# S3 경로 설정 (날짜별 디렉토리 구조)
from datetime import datetime

# ⚠️ 주의: 아래 상수들은 모듈 로드 시점의 날짜로 고정됩니다.
# 실제 업로드 시에는 S3Uploader.upload_data() 내부에서 동적으로 날짜를 계산합니다.
# 이 상수들은 레거시 메서드(upload_pdf, upload_json 등)에서만 사용되며,
# 현재 main.py에서는 사용되지 않습니다.
CRAWL_DATE = datetime.now().strftime("%Y-%m-%d")  # 크롤링 날짜 (⚠️ 모듈 로드 시점에 고정됨)

# S3 경로: datasets/{YYYY-MM-DD}/pdf|json/ (⚠️ 레거시 용도)
S3_BASE_PREFIX = f"datasets/{CRAWL_DATE}/"
S3_PDF_PREFIX = f"{S3_BASE_PREFIX}pdf/"
S3_JSON_PREFIX = f"{S3_BASE_PREFIX}json/"
S3_METADATA_PREFIX = "datasets/metadata/"  # 메타데이터는 날짜 구분 없음

print(f"📁 S3 구조 (레거시): {S3_PDF_PREFIX}, {S3_JSON_PREFIX}")
print(f"📅 모듈 로드 날짜: {CRAWL_DATE}")

# 사람인 크롤링 URL 파라미터
SARAMIN_BASE_URL = "https://www.saramin.co.kr/zf_user/jobs/public/list"
SARAMIN_PARAMS = {
    # 파라미터 없음 (디폴트가 최신순 정렬)
    # 모든 채용공고 크롤링 후 LLM/Ingestion 단계에서 필터링
}


def validate_config():
    """필수 환경변수 검증"""
    required_vars = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "S3_BUCKET_NAME": S3_BUCKET_NAME,
    }

    missing_vars = [key for key, value in required_vars.items() if not value]

    if missing_vars:
        raise EnvironmentError(
            f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}\n"
            f".env 파일을 확인하세요."
        )

    print("✅ 환경변수 검증 완료")


if __name__ == "__main__":
    # 설정 테스트
    print("\n=== Crawler 설정 확인 ===\n")
    print(f"AWS Region: {AWS_DEFAULT_REGION}")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"Crawl Mode: {CRAWL_MODE}")
    print(f"Max Pages: {CRAWL_MAX_PAGES}")
    print(f"\nS3 경로:")
    print(f"  PDF: s3://{S3_BUCKET_NAME}/{S3_PDF_PREFIX}")
    print(f"  JSON: s3://{S3_BUCKET_NAME}/{S3_JSON_PREFIX}")
    print()
    validate_config()
