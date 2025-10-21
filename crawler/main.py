"""
크롤러 메인 실행 파일 (최신순 정렬 + latest_rec_idx 비교)

1. S3에서 latest_rec_idx 로드
2. 최신순으로 크롤링 시작
3. 어제의 latest 발견 시 즉시 중단
4. S3 업로드
5. 오늘의 latest 업데이트
6. Ingestion API 자동 호출
"""

import sys
import os
import requests
from pathlib import Path

# src 모듈 import를 위한 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.saramin_crawler import SaraminCrawler
from src.s3_uploader import S3Uploader
from src.config import validate_config, CRAWL_MODE


def call_ingestion_api(rec_idx_list: list) -> bool:
    """
    Ingestion API 호출하여 신규 공고 처리

    Args:
        rec_idx_list: 신규 수집된 rec_idx 리스트

    Returns:
        bool: API 호출 성공 여부
    """
    if not rec_idx_list:
        print("⚠️  신규 공고가 없어 Ingestion API 호출을 건너뜁니다.")
        return True

    ingestion_url = os.getenv("INGESTION_SERVICE_URL", "http://ingestion:5002")
    endpoint = f"{ingestion_url}/process-new-data"

    print(f"\n{'='*60}")
    print("📡 Ingestion API 호출 중...")
    print(f"{'='*60}\n")
    print(f"🔗 URL: {endpoint}")
    print(f"📋 Payload: {len(rec_idx_list)}개 공고")

    try:
        response = requests.post(
            endpoint, json={"rec_idx_list": rec_idx_list}, timeout=300  # 5분 타임아웃
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Ingestion API 호출 성공!")
            print(f"   - 신규 추가: {result.get('added', 0)}개")
            print(f"   - 업데이트: {result.get('updated', 0)}개")
            print(f"   - 스킵: {result.get('skipped', 0)}개")
            print(f"   - 총 처리: {result.get('total_processed', 0)}개")
            return True
        else:
            print(f"\n❌ Ingestion API 호출 실패 (HTTP {response.status_code})")
            print(f"   응답: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Ingestion 서비스에 연결할 수 없습니다: {endpoint}")
        print("   Docker Compose 환경에서 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Ingestion API 호출 타임아웃 (5분 초과)")
        return False
    except Exception as e:
        print(f"\n❌ Ingestion API 호출 중 오류: {e}")
        return False


def main():
    """크롤러 메인 실행 함수 (최신순 정렬 + latest_rec_idx 비교 방식)"""

    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        Career-Hi RAG 크롤러 (최신순 최적화)             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    print(f"🔧 실행 모드: {CRAWL_MODE}")
    print(f"🔄 정렬: 최신순 (등록일 기준)")

    # 1. 환경변수 검증
    print(f"\n{'='*60}")
    print("1️⃣  환경변수 검증")
    print(f"{'='*60}\n")

    try:
        validate_config()
    except EnvironmentError as e:
        print(f"\n❌ {e}")
        return False

    # 2. S3 업로더 초기화 및 latest_rec_idx 로드
    print(f"\n{'='*60}")
    print("2️⃣  S3에서 이전 latest_rec_idx 로드")
    print(f"{'='*60}\n")

    try:
        uploader = S3Uploader()
    except Exception as e:
        print(f"\n❌ S3 업로더 초기화 실패: {e}")
        return False

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
    else:  # daily
        max_pages = 50
        max_posts_per_page = 100
        print("\n📅 일일 모드: 최대 10페이지, 100개 공고 수집")

    # 4. 크롤링 실행 (최신순 정렬)
    print(f"\n{'='*60}")
    print("3️⃣  크롤링 실행 (최신순 정렬)")
    print(f"{'='*60}\n")

    crawler = SaraminCrawler(headless=True)

    # 크롤링 시작 (previous_latest 전달)
    results = crawler.crawl_with_latest_stop(
        max_pages=max_pages,
        max_posts_per_page=max_posts_per_page,
        previous_latest_rec_idx=previous_latest,
    )

    successful_results = [r for r in results if r.get("status") == "success"]
    stopped_at_latest = crawler.stopped_at_latest  # 크롤러에서 설정된 플래그

    print(f"\n📊 크롤링 결과:")
    print(f"   - 신규 수집: {len(successful_results)}개")
    if stopped_at_latest:
        print(f"   - 중단 이유: 어제의 latest_rec_idx 발견!")
    print(f"   - 총 확인: {len(results)}개")

    # 5. 오늘의 latest_rec_idx 결정
    today_latest = None
    if successful_results:
        # 첫 번째 결과가 오늘의 최신
        today_latest = successful_results[0]["rec_idx"]
        print(f"\n🎯 오늘의 latest_rec_idx: {today_latest}")

    # 6. S3 업로드 (메모리에서 직접)
    new_rec_ids = []

    if successful_results:
        print(f"\n{'='*60}")
        print("4️⃣  S3 업로드 (메모리에서 직접)")
        print(f"{'='*60}\n")

        upload_success_count = 0
        upload_fail_count = 0

        for result in successful_results:
            rec_idx = result["rec_idx"]
            pdf_data = result["pdf_data"]
            metadata = result["metadata"]

            print(f"📤 {rec_idx} 업로드 중...")

            pdf_success, json_success = uploader.upload_data(
                pdf_data, metadata, rec_idx
            )

            if pdf_success and json_success:
                upload_success_count += 1
                new_rec_ids.append(rec_idx)
                print(f"   ✅ 완료")
            else:
                upload_fail_count += 1
                print(f"   ❌ 실패")

        print(
            f"\n📤 S3 업로드 완료: {upload_success_count}개 성공, {upload_fail_count}개 실패"
        )
    else:
        print("\n⚠️  신규 수집된 공고가 없어 S3 업로드를 건너뜁니다.")

    # 7. latest_rec_idx 업데이트 (오늘의 최신으로)
    if today_latest:
        print(f"\n{'='*60}")
        print("5️⃣  latest_rec_idx 업데이트")
        print(f"{'='*60}\n")

        if uploader.save_latest_rec_idx(today_latest):
            print(f"✅ latest_rec_idx 저장 완료: {today_latest}")
        else:
            print(f"⚠️  latest_rec_idx 저장 실패 (다음 실행 시 재시도됩니다)")

    # 8. Ingestion API 호출
    if new_rec_ids:
        ingestion_success = call_ingestion_api(new_rec_ids)
    else:
        print(f"\n{'='*60}")
        print("📡 Ingestion API 호출 건너뛰기")
        print(f"{'='*60}")
        print("   이유: 신규 수집된 공고가 없습니다.")
        ingestion_success = True

    # 9. 최종 결과
    print(f"\n{'='*60}")
    print("🎯 최종 결과")
    print(f"{'='*60}")
    print(f"\n📊 크롤링:")
    print(f"   - 신규 수집: {len(successful_results)}개")
    if previous_latest:
        print(f"   - 비교 기준: {previous_latest}")
    if stopped_at_latest:
        print(f"   - 조기 중단: ✅ (효율적!)")

    if successful_results:
        print(f"\n📤 S3 업로드:")
        print(f"   - 성공: {upload_success_count}개")
        print(f"   - 실패: {upload_fail_count}개")

    if new_rec_ids:
        print(f"\n📡 Ingestion API:")
        print(f"   - 상태: {'✅ 성공' if ingestion_success else '❌ 실패'}")
        print(f"   - 처리 대상: {len(new_rec_ids)}개")

    if today_latest:
        print(f"\n🎯 latest_rec_idx:")
        print(f"   - 저장됨: {today_latest}")

    overall_success = (
        not successful_results or upload_success_count > 0
    ) and ingestion_success

    if overall_success:
        print("\n✅ 크롤링 작업 완료!")
    else:
        print("\n⚠️  일부 작업이 실패했습니다. 로그를 확인하세요.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
