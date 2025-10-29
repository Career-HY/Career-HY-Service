"""
사람인 크롤러 모듈

채용공고 크롤링 및 메모리 내 처리 (S3 직접 업로드)
"""
import os
import time
import random
import base64
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import logging

from .config import (
    SARAMIN_BASE_URL,
    SARAMIN_PARAMS,
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
        self.existing_rec_ids = set()  # 기존 공고 ID (중복 체크용)
        self.new_rec_ids = []  # 이번 크롤링에서 새로 수집된 rec_idx
        self.stopped_at_latest = False  # latest_rec_idx 발견으로 중단되었는지 플래그

    def create_driver(self) -> webdriver.Chrome:
        """Chrome/Chromium 드라이버 생성"""
        chrome_options = Options()

        # Headless 모드 설정
        if self.headless:
            chrome_options.add_argument('--headless=new')  # 최신 headless 모드

        # Docker/EC2 환경을 위한 필수 옵션들
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-first-run')

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        # Docker 환경에서 Chromium 사용
        if os.path.exists('/usr/bin/chromium'):
            chrome_options.binary_location = '/usr/bin/chromium'
            logger.info("✅ Chromium 바이너리 감지 (Docker 환경)")

        logger.info("✅ Chrome 드라이버 생성 중...")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ 드라이버 생성 완료 (시스템 ChromeDriver 사용)")
            return driver
        except Exception as e:
            logger.error(f"❌ ChromeDriver 실행 실패: {e}")
            raise

    def parse_deadline_to_standard_format(self, deadline_text: str) -> str:
        """
        사람인 마감일 텍스트를 YYYY-MM-DD 형식으로 변환

        Args:
            deadline_text: 사람인 마감일 텍스트
                예: "2025.11.06 17:00", "~ 01/31(금)", "상시채용"

        Returns:
            str: YYYY-MM-DD 형식 날짜

        Examples:
            "2025.11.06 17:00" → "2025-11-06"
            "~ 01/31(금)" → "2025-01-31"
            "상시채용" → "9999-12-31"
        """
        try:
            # 상시채용 또는 채용시까지인 경우
            if "상시" in deadline_text or "채용시" in deadline_text or "미정" in deadline_text:
                logger.info(f"   📅 마감일: 상시채용 → 9999-12-31로 설정")
                return "9999-12-31"

            # 패턴 1: "2025.11.06 17:00" 형식 (점으로 구분)
            match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', deadline_text)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                standard_format = f"{year:04d}-{month:02d}-{day:02d}"
                logger.info(f"   📅 마감일 파싱: {deadline_text} → {standard_format}")
                return standard_format

            # 패턴 2: "~ 01/31(금)" 형식 (슬래시로 구분, 연도 없음)
            match = re.search(r'(\d{2})/(\d{2})', deadline_text)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))

                # 현재 연도 기준 날짜 생성
                current_year = datetime.now().year
                deadline_date = datetime(current_year, month, day)

                # 만약 날짜가 과거라면 다음 연도로 설정
                if deadline_date < datetime.now():
                    deadline_date = datetime(current_year + 1, month, day)

                standard_format = deadline_date.strftime('%Y-%m-%d')
                logger.info(f"   📅 마감일 파싱: {deadline_text} → {standard_format}")
                return standard_format

            # 파싱 실패
            logger.warning(f"   ⚠️  마감일 파싱 실패: {deadline_text} → 기본값 사용")
            default_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            return default_date

        except Exception as e:
            logger.error(f"   ❌ 마감일 파싱 오류: {deadline_text}, 에러: {e}")
            # 오류 시 30일 후로 설정
            default_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            return default_date

    def load_existing_rec_ids(self):
        """S3에서 활성 공고 목록 로드 (중복 체크용)"""
        try:
            from .s3_uploader import S3Uploader

            logger.info("\n📋 S3에서 활성 공고 목록 로딩 중...")
            uploader = S3Uploader()
            self.existing_rec_ids = uploader.list_active_rec_ids()
            logger.info(f"✅ 활성 공고 {len(self.existing_rec_ids)}개 확인됨\n")

        except Exception as e:
            logger.warning(f"⚠️  기존 공고 목록 로드 실패: {e}")
            logger.warning(f"⚠️  중복 체크 없이 진행합니다.\n")
            self.existing_rec_ids = set()

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
        logger.info(f"🔗 URL: {url}")

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
            import traceback
            logger.error(traceback.format_exc())
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

            # 마감일 추출 및 표준 형식 변환
            try:
                deadline_sel = (
                    f"#content > div.wrap_jview > section.jview.jview-0-{rec_idx} "
                    "> div.wrap_jv_cont > div.jv_cont.jv_howto "
                    "> div > div > dl > dd:nth-child(4)"
                )
                deadline_raw = self.driver.find_element(By.CSS_SELECTOR, deadline_sel).text.strip()
                logger.info(f"⏰ 마감일 (원본): {deadline_raw}")

                # 표준 형식으로 변환 (YYYY-MM-DD)
                deadline_standard = self.parse_deadline_to_standard_format(deadline_raw)

            except Exception as e:
                logger.warning(f"⚠️  마감일 추출 실패: {e}")
                deadline_raw = "미정"
                deadline_standard = self.parse_deadline_to_standard_format("미정")

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

            # PDF 데이터를 메모리에서 생성 (로컬 저장 없음)
            logger.info(f"📄 PDF 데이터 생성 중...")
            pdf = self.driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
            pdf_data = base64.b64decode(pdf['data'])
            logger.info(f"✅ PDF 데이터 생성 완료")

            # 메타데이터 생성 (로컬 저장 없음)
            metadata = {
                "rec_idx": rec_idx,
                "post_title": post_title,
                "start_date": start_date,
                "deadline_raw": deadline_raw,  # 원본 마감일 텍스트
                "deadline": deadline_standard,  # 표준 형식 (YYYY-MM-DD)
                "detail_url": detail_url,
                "crawling_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            logger.info(f"🎉 {rec_idx} 크롤링 완료!")

            return {
                "rec_idx": rec_idx,
                "post_title": post_title,
                "start_date": start_date,
                "deadline_raw": deadline_raw,
                "deadline": deadline_standard,
                "detail_url": detail_url,
                "pdf_data": pdf_data,  # PDF 바이너리 데이터
                "metadata": metadata,  # 메타데이터 딕셔너리
                "status": "success"
            }

        except Exception as e:
            logger.error(f"❌ {rec_idx} 크롤링 실패: {e}")
            return {
                "rec_idx": rec_idx,
                "status": "failed",
                "error": str(e)
            }

    def get_successful_results(self) -> List[Dict]:
        """성공한 크롤링 결과만 반환"""
        return [r for r in self.results if r.get('status') == 'success']

    def get_failed_results(self) -> List[Dict]:
        """실패한 크롤링 결과만 반환"""
        return [r for r in self.results if r.get('status') == 'failed']

    def get_skipped_results(self) -> List[Dict]:
        """중복으로 스킵된 결과만 반환"""
        return [r for r in self.results if r.get('status') == 'skipped_duplicate']

    def get_new_rec_ids(self) -> List[str]:
        """이번 크롤링에서 새로 수집된 rec_idx 목록 반환 (Ingestion API 전달용)"""
        return self.new_rec_ids


if __name__ == "__main__":
    # 크롤러 테스트
    print("\n=== Saramin Crawler 테스트 ===\n")

    crawler = SaraminCrawler(headless=True)
    results = crawler.crawl(max_pages=1, max_posts_per_page=3)

    print("\n✅ 크롤러 테스트 완료")
    print(f"수집된 공고 수: {len(crawler.get_successful_results())}개")
