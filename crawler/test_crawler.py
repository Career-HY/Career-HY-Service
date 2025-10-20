"""
사람인 크롤링 테스트 스크립트
- 1페이지만 크롤링
- 최대 3개 공고만 수집
- PDF + JSON 메타데이터 저장
"""

import os
import time
import random
import base64
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def create_driver():
    """Chrome 드라이버 생성 (headless 모드)"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )

    print("✅ Chrome 드라이버 생성 중...")

    # ChromeDriver 자동 탐지 (시스템에 설치된 Chrome 사용)
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ 드라이버 생성 완료 (시스템 ChromeDriver 사용)")
    except Exception as e:
        print(f"⚠️  시스템 ChromeDriver 실패, webdriver-manager 시도 중...")
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ 드라이버 생성 완료 (webdriver-manager 사용)")

    return driver


def print_to_pdf(driver, file_path):
    """현재 페이지를 PDF로 저장"""
    pdf = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
    pdf_data = base64.b64decode(pdf["data"])
    with open(file_path, "wb") as f:
        f.write(pdf_data)


def test_crawl(max_posts=3):
    """
    테스트 크롤링 실행

    Args:
        max_posts: 수집할 최대 공고 수 (기본값: 3)
    """
    # 출력 디렉토리 생성
    pdf_dir = "test_output/pdf"
    meta_dir = "test_output/metadata"
    for d in (pdf_dir, meta_dir):
        os.makedirs(d, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🕷️  사람인 크롤링 테스트 시작 (최대 {max_posts}개 공고)")
    print(f"{'='*60}\n")

    driver = None
    try:
        driver = create_driver()

        # 1페이지만 크롤링
        page = 1
        url = (
            "https://www.saramin.co.kr/zf_user/jobs/public/list?"
            "exp_cd=1&edu_min=8&edu_max=11&company_cd=0,1,2,3,4,5,6,7,9,10"
            "&panel_type=domestic&search_optional_item=y&search_done=y"
            f"&panel_count=y&preview=y&page={page}&isAjaxRequest=y"
        )

        print(f"📄 페이지 {page} 접속 중...")
        print(f"   URL: {url[:80]}...")

        driver.get(url)
        time.sleep(random.uniform(3, 5))
        print("✅ 페이지 로드 완료\n")

        # 채용공고 링크 추출
        print("🔍 채용공고 링크 추출 중...")
        elems = driver.find_elements(By.CSS_SELECTOR, "a[id^='rec_link_']")

        if not elems:
            print("❌ 채용공고 링크를 찾을 수 없습니다.")
            print("   사람인 사이트 구조가 변경되었을 수 있습니다.")
            return False

        print(f"✅ {len(elems)}개의 채용공고 링크 발견")

        # 공고 리스트 생성 (최대 max_posts개)
        posts = []
        for el in elems[:max_posts]:
            rid = el.get_attribute("id").replace("rec_link_", "")
            href = el.get_attribute("href")
            posts.append((rid, href))

        print(f"📋 수집 대상: {len(posts)}개 공고\n")

        # 각 공고 상세 정보 수집
        success_count = 0
        for idx, (rec_idx, detail_url) in enumerate(posts, 1):
            print(f"\n{'─'*60}")
            print(f"📌 [{idx}/{len(posts)}] rec_idx: {rec_idx}")
            print(f"{'─'*60}")

            try:
                # 상세 페이지 접속
                print(f"🌐 상세 페이지 접속 중...")
                driver.get(detail_url)
                time.sleep(random.uniform(4, 6))
                print(f"✅ 페이지 로드 완료")

                # 제목 추출
                try:
                    title_sel = (
                        f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                        "> div.wrap_jv_cont > div.wrap_jv_header > div > h1"
                    )
                    post_title = driver.find_element(
                        By.CSS_SELECTOR, title_sel
                    ).text.strip()
                    print(f"📝 제목: {post_title}")
                except Exception as e:
                    print(f"⚠️  제목 추출 실패: {e}")
                    post_title = "제목 없음"

                # 시작일 추출
                try:
                    start_sel = (
                        f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                        "> div.wrap_jv_cont > div.jv_cont.jv_howto "
                        "> div > div > dl > dd:nth-child(2)"
                    )
                    start_date = driver.find_element(
                        By.CSS_SELECTOR, start_sel
                    ).text.strip()
                    print(f"📅 시작일: {start_date}")
                except Exception as e:
                    print(f"⚠️  시작일 추출 실패: {e}")
                    start_date = "미정"

                # 마감일 추출
                try:
                    deadline_sel = (
                        f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                        "> div.wrap_jv_cont > div.jv_cont.jv_howto "
                        "> div > div > dl > dd:nth-child(4)"
                    )
                    deadline = driver.find_element(
                        By.CSS_SELECTOR, deadline_sel
                    ).text.strip()
                    print(f"⏰ 마감일: {deadline}")
                except Exception as e:
                    print(f"⚠️  마감일 추출 실패: {e}")
                    deadline = "미정"

                # 불필요한 요소 제거 (PDF 저장용)
                print(f"🧹 불필요한 요소 제거 중...")
                js = f"""
                    var removals = [
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont > div.jv_cont.jv_howto",
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont > div.jv_cont.jv_statics",
                      "#hot100-top10-list-{rec_idx}",
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont > div.self_introduce",
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont > div.jv_cont.jv_insatong",
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont > div.banner_job_package.bottom"
                    ];
                    removals.forEach(function(sel){{
                      var e = document.querySelector(sel);
                      if(e) e.remove();
                    }});
                    var c = document.querySelector(
                      "#content > div.wrap_jview > section.jview.jview-0-{rec_idx} > div.wrap_jv_cont"
                    );
                    if(c) document.body.innerHTML = c.outerHTML;
                """
                driver.execute_script(js)
                time.sleep(1)

                # PDF 저장
                pdf_file = os.path.join(pdf_dir, f"{rec_idx}.pdf")
                print(f"💾 PDF 저장 중: {pdf_file}")
                print_to_pdf(driver, pdf_file)
                print(f"✅ PDF 저장 완료")

                # 메타데이터 JSON 저장
                json_file = os.path.join(meta_dir, f"{rec_idx}.json")
                meta = {
                    "rec_idx": rec_idx,
                    "post_title": post_title,
                    "start_date": start_date,
                    "deadline": deadline,
                    "detail_url": detail_url,
                    "crawling_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                print(f"💾 메타데이터 저장 중: {json_file}")
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                print(f"✅ 메타데이터 저장 완료")

                success_count += 1
                print(f"\n🎉 [{idx}/{len(posts)}] 수집 완료!")

                # 다음 공고 전 대기
                if idx < len(posts):
                    wait_time = random.uniform(2, 4)
                    print(f"⏳ {wait_time:.1f}초 대기 중...")
                    time.sleep(wait_time)

            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")
                print(f"   공고 {rec_idx} 수집 실패. 다음 공고로 넘어갑니다.")
                continue

        # 최종 결과
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 테스트 완료!")
        print(f"{'='*60}")
        print(f"📊 수집 결과:")
        print(f"   - 시도: {len(posts)}개")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {len(posts) - success_count}개")
        print(f"\n📁 출력 디렉토리:")
        print(f"   - PDF: {os.path.abspath(pdf_dir)}")
        print(f"   - JSON: {os.path.abspath(meta_dir)}")
        print(f"{'='*60}\n")

        return success_count > 0

    except Exception as e:
        print(f"\n❌ 크롤링 중 치명적 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if driver:
            print("🔌 브라우저 종료 중...")
            driver.quit()
            print("✅ 브라우저 종료 완료")


if __name__ == "__main__":
    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       사람인 크롤러 테스트 스크립트                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    # 크롤링 실행
    success = test_crawl(max_posts=3)

    if success:
        print("\n✅ 테스트 성공! 출력 파일을 확인하세요.")
        print("   다음 단계: S3 업로드 기능 구현")
    else:
        print("\n❌ 테스트 실패. 에러 메시지를 확인하세요.")
        print("   사람인 사이트 구조가 변경되었을 수 있습니다.")
