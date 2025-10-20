"""
크롤링 + S3 업로드 통합 테스트

1. 사람인 크롤링 (1페이지, 3개 공고)
2. 로컬 저장 (PDF + JSON)
3. S3 업로드
4. S3 확인
"""
import sys
from pathlib import Path

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.saramin_crawler import SaraminCrawler
from src.s3_uploader import S3Uploader
from src.config import validate_config


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       크롤링 + S3 업로드 통합 테스트                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 1. 환경변수 검증
    print("\n" + "="*60)
    print("1️⃣  환경변수 검증")
    print("="*60 + "\n")

    try:
        validate_config()
    except EnvironmentError as e:
        print(f"\n❌ {e}")
        return False

    # 2. 크롤링 실행
    print("\n" + "="*60)
    print("2️⃣  크롤링 실행")
    print("="*60 + "\n")

    crawler = SaraminCrawler(headless=True)
    results = crawler.crawl(max_pages=1, max_posts_per_page=3)

    successful_results = crawler.get_successful_results()

    if not successful_results:
        print("\n❌ 크롤링 실패. S3 업로드를 건너뜁니다.")
        return False

    print(f"\n✅ {len(successful_results)}개 공고 크롤링 성공")

    # 3. S3 업로드
    print("\n" + "="*60)
    print("3️⃣  S3 업로드")
    print("="*60 + "\n")

    try:
        uploader = S3Uploader()
    except Exception as e:
        print(f"\n❌ S3 업로더 초기화 실패: {e}")
        return False

    upload_success_count = 0
    upload_fail_count = 0

    for result in successful_results:
        rec_idx = result['rec_idx']
        pdf_path = result['pdf_path']
        json_path = result['json_path']

        print(f"\n📤 {rec_idx} 업로드 중...")

        # S3에 이미 존재하는지 확인
        pdf_exists, json_exists = uploader.check_rec_idx_exists(rec_idx)

        if pdf_exists and json_exists:
            print(f"⚠️  {rec_idx}는 이미 S3에 존재합니다. 덮어쓰기 진행...")

        # 업로드 실행
        pdf_success, json_success = uploader.upload_pair(pdf_path, json_path, rec_idx)

        if pdf_success and json_success:
            upload_success_count += 1
            print(f"✅ {rec_idx} 업로드 완료")
        else:
            upload_fail_count += 1
            print(f"❌ {rec_idx} 업로드 실패")

    # 4. 최종 결과
    print("\n" + "="*60)
    print("4️⃣  최종 결과")
    print("="*60)
    print(f"\n📊 크롤링:")
    print(f"   - 성공: {len(successful_results)}개")
    print(f"   - 실패: {len(results) - len(successful_results)}개")
    print(f"\n📤 S3 업로드:")
    print(f"   - 성공: {upload_success_count}개")
    print(f"   - 실패: {upload_fail_count}개")

    if upload_success_count == len(successful_results):
        print("\n✅ 통합 테스트 성공!")
        print("\n📋 다음 단계:")
        print("   1. AWS S3 콘솔에서 파일 확인")
        print("   2. Ingestion API 증분 업데이트 구현")
        print("   3. Crawler ↔ Ingestion 통합")
        return True
    else:
        print("\n⚠️  일부 업로드 실패. S3 설정을 확인하세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
