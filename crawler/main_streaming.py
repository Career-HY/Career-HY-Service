"""
크롤러 메인 실행 파일 (스트리밍 방식 - 메모리 효율적)

배치 처리:
1. 10개씩 크롤링 → S3 업로드 → Ingestion API 호출 → 메모리 해제
2. 메모리 사용량: 1000개 → 10개 (100배 절감)
"""

import sys
import os
import requests
from pathlib import Path

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.saramin_crawler import SaraminCrawler
from src.s3_uploader import S3Uploader
from src.config import validate_config, CRAWL_MODE, CRAWL_MAX_PAGES

# 배치 크기 설정
UPLOAD_BATCH_SIZE = 10  # 10개씩 S3 업로드 후 API 호출


def call_ingestion_api_batch(rec_idx_list: list) -> bool:
    """
    Ingestion API 호출하여 신규 공고 처리 (배치)

    Args:
        rec_idx_list: 신규 수집된 rec_idx 리스트

    Returns:
        bool: API 호출 성공 여부
    """
    if not rec_idx_list:
        return True

    ingestion_url = os.getenv("INGESTION_SERVICE_URL", "http://ingestion:5002")
    endpoint = f"{ingestion_url}/process-new-data"

    print(f"📡 Ingestion API 호출: {len(rec_idx_list)}개 공고")

    try:
        response = requests.post(
            endpoint, json={"rec_idx_list": rec_idx_list}, timeout=300
        )

        if response.status_code == 200:
            print(f"   ✅ API 호출 성공")
            return True
        else:
            print(f"   ❌ API 호출 실패: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ API 호출 오류: {e}")
        return False


def main():
    """크롤러 메인 실행 함수 (스트리밍 방식)"""

    print(f"\n{'='*60}")
    print("🚀 Career-Hi 크롤러 시작 (스트리밍 방식)")
    print(f"{'='*60}\n")

    # 1. 환경변수 검증
    validate_config()

    # 2. S3 업로더 초기화 및 latest_rec_idx 로드
    uploader = S3Uploader()
    previous_latest = uploader.get_latest_rec_idx()

    if previous_latest:
        print(f"📌 이전 크롤링 최신 공고: {previous_latest}")
        print(f"   → 이 공고를 만나면 크롤링 중단!")
    else:
        print(f"🆕 첫 실행입니다. 전체 크롤링을 진행합니다.")

    # 3. 크롤링 설정
    if CRAWL_MODE == "test":
        max_pages = 1
        max_posts_per_page = 5
        print("\n📝 테스트 모드: 1페이지, 5개 공고만 수집")
    else:  # daily or initial
        max_pages = CRAWL_MAX_PAGES
        max_posts_per_page = 100
        print(
            f"\n📅 크롤링 모드: 최대 {max_pages}페이지 (CRAWL_MAX_PAGES={CRAWL_MAX_PAGES})"
        )

    # 4. 크롤러 초기화
    crawler = SaraminCrawler(headless=True)

    # 5. 스트리밍 크롤링 시작
    print(f"\n{'='*60}")
    print("🕷️  스트리밍 크롤링 시작")
    print(f"{'='*60}\n")

    today_latest = None
    total_crawled = 0
    total_uploaded = 0
    batch_buffer = []  # 배치 버퍼
    batch_rec_ids = []  # 배치 rec_idx
    stopped_at_latest = False

    try:
        driver = crawler.create_driver()
        crawler.driver = driver

        for page in range(1, max_pages + 1):
            print(f"\n{'─'*60}")
            print(f"📄 페이지 {page}/{max_pages} 처리 중")
            print(f"{'─'*60}\n")

            # 채용공고 링크 추출
            posts = crawler.extract_job_links(page)

            if not posts:
                print(f"⚠️  페이지 {page}에서 공고를 찾지 못했습니다. 크롤링 종료.")
                break

            # max_posts_per_page 제한 적용
            if max_posts_per_page:
                posts = posts[:max_posts_per_page]

            # 각 공고 크롤링
            for idx, (rec_idx, detail_url) in enumerate(posts, 1):
                # latest_rec_idx 발견 시 중단
                if previous_latest and rec_idx == previous_latest:
                    print(f"🛑 어제의 latest_rec_idx 발견: {rec_idx}")
                    print(f"   → 크롤링 즉시 중단!")
                    stopped_at_latest = True
                    break

                # 크롤링
                print(f"🆕 {rec_idx} - 크롤링 중...")
                result = crawler.crawl_job_detail(rec_idx, detail_url)

                if result and result.get("status") == "success":
                    total_crawled += 1

                    # 첫 번째 공고를 오늘의 latest로 저장
                    if today_latest is None:
                        today_latest = rec_idx

                    # 즉시 S3 업로드
                    pdf_success, json_success = uploader.upload_data(
                        result["pdf_data"], result["metadata"], rec_idx
                    )

                    if pdf_success and json_success:
                        total_uploaded += 1
                        batch_rec_ids.append(rec_idx)
                        print(
                            f"   ✅ S3 업로드 완료 ({total_uploaded}/{total_crawled})"
                        )

                        # 배치가 차면 Ingestion API 호출
                        if len(batch_rec_ids) >= UPLOAD_BATCH_SIZE:
                            print(
                                f"\n💾 배치 {len(batch_rec_ids)}개 → Ingestion API 호출"
                            )
                            call_ingestion_api_batch(batch_rec_ids)
                            batch_rec_ids = []  # 메모리 해제
                            print()
                    else:
                        print(f"   ❌ S3 업로드 실패")

                    # result 메모리 해제
                    del result

            # latest 발견으로 중단되었으면 페이지 순회도 중단
            if stopped_at_latest:
                break

        # 6. 남은 배치 처리
        if batch_rec_ids:
            print(f"\n💾 남은 배치 {len(batch_rec_ids)}개 → Ingestion API 호출")
            call_ingestion_api_batch(batch_rec_ids)

        # 7. latest_rec_idx 업데이트
        if today_latest:
            print(f"\n{'='*60}")
            print("5️⃣  latest_rec_idx 업데이트")
            print(f"{'='*60}\n")

            if uploader.save_latest_rec_idx(today_latest):
                print(f"✅ latest_rec_idx 저장 완료: {today_latest}")
            else:
                print(f"⚠️  latest_rec_idx 저장 실패")

        # 8. 최종 결과
        print(f"\n{'='*60}")
        print("🎯 최종 결과")
        print(f"{'='*60}")
        print(f"\n📊 크롤링:")
        print(f"   - 신규 수집: {total_crawled}개")
        print(f"   - S3 업로드: {total_uploaded}개")
        if stopped_at_latest:
            print(f"   - 중단 이유: 이전 latest 발견")
        print(f"\n✅ 스트리밍 크롤링 완료!")

        return True

    except Exception as e:
        print(f"\n❌ 크롤링 오류: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # 브라우저 종료
        if hasattr(crawler, "driver") and crawler.driver:
            crawler.driver.quit()
            print("\n🔌 브라우저 종료 완료")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
