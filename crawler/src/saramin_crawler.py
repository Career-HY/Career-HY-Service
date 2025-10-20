"""
사람인 크롤러 모듈

채용공고 크롤링 및 로컬 저장
"""
import os
import time
import random
import base64
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import logging

from .config import (
    SARAMIN_BASE_URL,
    SARAMIN_PARAMS,
    LOCAL_PDF_DIR,
    LOCAL_JSON_DIR,
    CRAWL_MAX_PAGES
)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SaraminCrawler:
    """사람인 채용공고 크롤러"""

    def __init__(self, headless: bool = True):
        """
        크롤러 초기화

        Args:
            headless: Chrome 헤드리스 모드 사용 여부
        """
        self.headless = headless
        self.driver = None
        self.results = []

    def create_driver(self) -> webdriver.Chrome:
        """Chrome 드라이버 생성"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        logger.info("✅ Chrome 드라이버 생성 중...")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ 드라이버 생성 완료 (시스템 ChromeDriver 사용)")
        except Exception as e:
            logger.warning(f"⚠️  시스템 ChromeDriver 실패, webdriver-manager 시도 중...")
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ 드라이버 생성 완료 (webdriver-manager 사용)")

        return driver

    def print_to_pdf(self, driver: webdriver.Chrome, file_path: str) -> None:
        """현재 페이지를 PDF로 저장"""
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
        pdf_data = base64.b64decode(pdf['data'])
        with open(file_path, "wb") as f:
            f.write(pdf_data)

    def build_list_url(self, page: int) -> str:
        """채용공고 목록 URL 생성"""
        params = SARAMIN_PARAMS.copy()
        params['page'] = str(page)
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{SARAMIN_BASE_URL}?{param_str}"

    def extract_job_links(self, page: int) -> List[Tuple[str, str]]:
        """
        특정 페이지에서 채용공고 링크 추출

        Args:
            page: 페이지 번호

        Returns:
            List[Tuple[str, str]]: [(rec_idx, detail_url), ...]
        """
        url = self.build_list_url(page)
        logger.info(f"📄 페이지 {page} 접속 중...")

        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            logger.info(f"✅ 페이지 {page} 로드 완료")

            # 채용공고 링크 추출
            elems = self.driver.find_elements(By.CSS_SELECTOR, "a[id^='rec_link_']")

            if not elems:
                logger.warning(f"⚠️  페이지 {page}에서 채용공고 링크를 찾지 못했습니다.")
                return []

            posts = []
            for el in elems:
                rec_idx = el.get_attribute("id").replace("rec_link_", "")
                href = el.get_attribute("href")
                posts.append((rec_idx, href))

            logger.info(f"✅ {len(posts)}개의 채용공고 링크 발견")
            return posts

        except Exception as e:
            logger.error(f"❌ 페이지 {page} 접속 실패: {e}")
            return []

    def crawl_job_detail(self, rec_idx: str, detail_url: str) -> Optional[Dict]:
        """
        채용공고 상세 정보 크롤링

        Args:
            rec_idx: 채용공고 ID
            detail_url: 상세 페이지 URL

        Returns:
            Optional[Dict]: 크롤링 결과 또는 None (실패 시)
        """
        logger.info(f"📌 rec_idx: {rec_idx} 크롤링 시작")

        try:
            # 상세 페이지 접속
            self.driver.get(detail_url)
            time.sleep(random.uniform(4, 6))

            # 제목 추출
            try:
                title_sel = (
                    f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                    "> div.wrap_jv_cont > div.wrap_jv_header > div > h1"
                )
                post_title = self.driver.find_element(By.CSS_SELECTOR, title_sel).text.strip()
                logger.info(f"📝 제목: {post_title}")
            except Exception as e:
                logger.warning(f"⚠️  제목 추출 실패: {e}")
                post_title = "제목 없음"

            # 시작일 추출
            try:
                start_sel = (
                    f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                    "> div.wrap_jv_cont > div.jv_cont.jv_howto "
                    "> div > div > dl > dd:nth-child(2)"
                )
                start_date = self.driver.find_element(By.CSS_SELECTOR, start_sel).text.strip()
                logger.info(f"📅 시작일: {start_date}")
            except Exception as e:
                logger.warning(f"⚠️  시작일 추출 실패: {e}")
                start_date = "미정"

            # 마감일 추출
            try:
                deadline_sel = (
                    f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                    "> div.wrap_jv_cont > div.jv_cont.jv_howto "
                    "> div > div > dl > dd:nth-child(4)"
                )
                deadline = self.driver.find_element(By.CSS_SELECTOR, deadline_sel).text.strip()
                logger.info(f"⏰ 마감일: {deadline}")
            except Exception as e:
                logger.warning(f"⚠️  마감일 추출 실패: {e}")
                deadline = "미정"

            # 불필요한 요소 제거 (PDF 생성용)
            logger.info(f"🧹 불필요한 요소 제거 중...")
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
            self.driver.execute_script(js)
            time.sleep(1)

            # PDF 저장
            pdf_path = LOCAL_PDF_DIR / f"{rec_idx}.pdf"
            logger.info(f"💾 PDF 저장 중: {pdf_path}")
            self.print_to_pdf(self.driver, str(pdf_path))
            logger.info(f"✅ PDF 저장 완료")

            # 메타데이터 JSON 저장
            json_path = LOCAL_JSON_DIR / f"{rec_idx}.json"
            metadata = {
                "rec_idx": rec_idx,
                "post_title": post_title,
                "start_date": start_date,
                "deadline": deadline,
                "detail_url": detail_url,
                "crawling_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            logger.info(f"💾 메타데이터 저장 중: {json_path}")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 메타데이터 저장 완료")

            logger.info(f"🎉 {rec_idx} 크롤링 완료!")

            return {
                "rec_idx": rec_idx,
                "post_title": post_title,
                "start_date": start_date,
                "deadline": deadline,
                "detail_url": detail_url,
                "pdf_path": str(pdf_path),
                "json_path": str(json_path),
                "success": True
            }

        except Exception as e:
            logger.error(f"❌ {rec_idx} 크롤링 실패: {e}")
            return {
                "rec_idx": rec_idx,
                "success": False,
                "error": str(e)
            }

    def crawl(self, max_pages: Optional[int] = None, max_posts_per_page: Optional[int] = None) -> List[Dict]:
        """
        크롤링 실행

        Args:
            max_pages: 최대 크롤링할 페이지 수 (None이면 설정 파일 값 사용)
            max_posts_per_page: 페이지당 최대 크롤링할 공고 수 (None이면 전체)

        Returns:
            List[Dict]: 크롤링 결과 리스트
        """
        if max_pages is None:
            max_pages = CRAWL_MAX_PAGES

        logger.info(f"\n{'='*60}")
        logger.info(f"🕷️  사람인 크롤링 시작 (최대 {max_pages}페이지)")
        logger.info(f"{'='*60}\n")

        self.results = []

        try:
            self.driver = self.create_driver()

            for page in range(1, max_pages + 1):
                logger.info(f"\n{'─'*60}")
                logger.info(f"📄 페이지 {page}/{max_pages} 처리 중")
                logger.info(f"{'─'*60}\n")

                # 채용공고 링크 추출
                posts = self.extract_job_links(page)

                if not posts:
                    logger.warning(f"⚠️  페이지 {page}에서 공고를 찾지 못했습니다. 크롤링 종료.")
                    break

                # max_posts_per_page 제한 적용
                if max_posts_per_page:
                    posts = posts[:max_posts_per_page]

                # 각 공고 크롤링
                for idx, (rec_idx, detail_url) in enumerate(posts, 1):
                    result = self.crawl_job_detail(rec_idx, detail_url)
                    if result:
                        self.results.append(result)

                    # 다음 공고 전 대기
                    if idx < len(posts):
                        wait_time = random.uniform(2, 4)
                        logger.info(f"⏳ {wait_time:.1f}초 대기 중...")
                        time.sleep(wait_time)

                # 다음 페이지 전 대기
                if page < max_pages:
                    wait_time = random.uniform(5, 10)
                    logger.info(f"\n⏳ 다음 페이지 전 {wait_time:.1f}초 대기 중...\n")
                    time.sleep(wait_time)

            # 최종 결과
            success_count = sum(1 for r in self.results if r.get('success'))
            fail_count = len(self.results) - success_count

            logger.info(f"\n{'='*60}")
            logger.info(f"✅ 크롤링 완료!")
            logger.info(f"{'='*60}")
            logger.info(f"📊 수집 결과:")
            logger.info(f"   - 성공: {success_count}개")
            logger.info(f"   - 실패: {fail_count}개")
            logger.info(f"   - 총합: {len(self.results)}개")
            logger.info(f"{'='*60}\n")

            return self.results

        except Exception as e:
            logger.error(f"\n❌ 크롤링 중 치명적 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return self.results

        finally:
            if self.driver:
                logger.info("🔌 브라우저 종료 중...")
                self.driver.quit()
                logger.info("✅ 브라우저 종료 완료")

    def get_successful_results(self) -> List[Dict]:
        """성공한 크롤링 결과만 반환"""
        return [r for r in self.results if r.get('success')]

    def get_failed_results(self) -> List[Dict]:
        """실패한 크롤링 결과만 반환"""
        return [r for r in self.results if not r.get('success')]


if __name__ == "__main__":
    # 크롤러 테스트
    print("\n=== Saramin Crawler 테스트 ===\n")

    crawler = SaraminCrawler(headless=True)
    results = crawler.crawl(max_pages=1, max_posts_per_page=3)

    print("\n✅ 크롤러 테스트 완료")
    print(f"수집된 공고 수: {len(crawler.get_successful_results())}개")
