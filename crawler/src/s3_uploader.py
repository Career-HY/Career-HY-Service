"""
S3 업로드 모듈

PDF 및 JSON 파일을 AWS S3에 업로드
"""
import os
import boto3
import json
from pathlib import Path
from typing import Optional, List, Set, Dict
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from io import BytesIO

from .config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_DEFAULT_REGION,
    S3_BUCKET_NAME,
    S3_METADATA_PREFIX,
    CRAWL_MODE
)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class S3Uploader:
    """S3 파일 업로드 클래스"""

    def __init__(self):
        """S3 클라이언트 초기화"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_DEFAULT_REGION
            )
            self.bucket_name = S3_BUCKET_NAME
            logger.info(f"✅ S3 클라이언트 초기화 완료 (버킷: {self.bucket_name})")
        except NoCredentialsError:
            logger.error("❌ AWS 자격 증명을 찾을 수 없습니다. 환경변수를 확인해주세요.")
            raise
        except Exception as e:
            logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
            raise

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        단일 파일을 S3에 업로드

        Args:
            local_path: 로컬 파일 경로
            s3_key: S3 객체 키 (버킷 내 경로)

        Returns:
            bool: 업로드 성공 여부
        """
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"✅ 업로드 성공: {s3_key}")
            return True
        except FileNotFoundError:
            logger.error(f"❌ 파일을 찾을 수 없음: {local_path}")
            return False
        except ClientError as e:
            logger.error(f"❌ S3 업로드 실패 ({s3_key}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류 ({s3_key}): {e}")
            return False

    def upload_pdf(self, local_pdf_path: str, rec_idx: str) -> bool:
        """
        PDF 파일을 S3에 업로드

        Args:
            local_pdf_path: 로컬 PDF 파일 경로
            rec_idx: 채용공고 ID

        Returns:
            bool: 업로드 성공 여부
        """
        s3_key = f"{S3_PDF_PREFIX}{rec_idx}.pdf"
        logger.info(f"📤 PDF 업로드 중: {rec_idx}.pdf → s3://{self.bucket_name}/{s3_key}")
        return self.upload_file(local_pdf_path, s3_key)

    def upload_json(self, local_json_path: str, rec_idx: str) -> bool:
        """
        JSON 메타데이터를 S3에 업로드

        Args:
            local_json_path: 로컬 JSON 파일 경로
            rec_idx: 채용공고 ID

        Returns:
            bool: 업로드 성공 여부
        """
        s3_key = f"{S3_JSON_PREFIX}{rec_idx}.json"
        logger.info(f"📤 JSON 업로드 중: {rec_idx}.json → s3://{self.bucket_name}/{s3_key}")
        return self.upload_file(local_json_path, s3_key)

    def upload_pair(self, pdf_path: str, json_path: str, rec_idx: str) -> tuple[bool, bool]:
        """
        PDF와 JSON을 함께 업로드 (기존 방식 - test/initial 모드용)

        Args:
            pdf_path: 로컬 PDF 파일 경로
            json_path: 로컬 JSON 파일 경로
            rec_idx: 채용공고 ID

        Returns:
            tuple[bool, bool]: (PDF 업로드 성공 여부, JSON 업로드 성공 여부)
        """
        pdf_success = self.upload_pdf(pdf_path, rec_idx)
        json_success = self.upload_json(json_path, rec_idx)

        if pdf_success and json_success:
            logger.info(f"🎉 {rec_idx} 업로드 완료 (PDF + JSON)")
        elif pdf_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (PDF만 업로드)")
        elif json_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (JSON만 업로드)")
        else:
            logger.error(f"❌ {rec_idx} 업로드 실패")

        return pdf_success, json_success

    def upload_pair_by_deadline(self, pdf_path: str, json_path: str, rec_idx: str, deadline: str) -> tuple[bool, bool]:
        """
        PDF와 JSON을 마감일 기준 경로로 업로드 (daily 모드용)

        Args:
            pdf_path: 로컬 PDF 파일 경로
            json_path: 로컬 JSON 파일 경로
            rec_idx: 채용공고 ID
            deadline: 마감일 (YYYY-MM-DD 형식)

        Returns:
            tuple[bool, bool]: (PDF 업로드 성공 여부, JSON 업로드 성공 여부)
        """
        # S3 경로: datasets/by-deadline/{deadline}/pdf/{rec_idx}.pdf
        pdf_s3_key = f"{S3_PDF_PREFIX}{deadline}/pdf/{rec_idx}.pdf"
        json_s3_key = f"{S3_JSON_PREFIX}{deadline}/json/{rec_idx}.json"

        logger.info(f"📤 마감일 기준 업로드: {rec_idx} → {deadline}/")

        pdf_success = self.upload_file(pdf_path, pdf_s3_key)
        json_success = self.upload_file(json_path, json_s3_key)

        if pdf_success and json_success:
            logger.info(f"🎉 {rec_idx} 업로드 완료 (마감일: {deadline})")
        elif pdf_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (PDF만 업로드)")
        elif json_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (JSON만 업로드)")
        else:
            logger.error(f"❌ {rec_idx} 업로드 실패")

        return pdf_success, json_success

    def upload_data(self, pdf_data: bytes, metadata: Dict, rec_idx: str) -> tuple[bool, bool]:
        """
        메모리의 PDF 데이터와 메타데이터를 S3에 직접 업로드 (로컬 저장 없음)

        Args:
            pdf_data: PDF 바이너리 데이터
            metadata: 메타데이터 딕셔너리
            rec_idx: 채용공고 ID

        Returns:
            tuple[bool, bool]: (PDF 업로드 성공 여부, JSON 업로드 성공 여부)
        """
        # 업로드 시점의 날짜 계산 (매번 새로 계산)
        crawl_date = datetime.now().strftime("%Y-%m-%d")

        # S3 경로: datasets/{YYYY-MM-DD}/pdf/{rec_idx}.pdf
        pdf_s3_key = f"datasets/{crawl_date}/pdf/{rec_idx}.pdf"
        json_s3_key = f"datasets/{crawl_date}/json/{rec_idx}.json"

        logger.info(f"📤 메모리에서 직접 업로드: {rec_idx} → {crawl_date}/")

        pdf_success = False
        json_success = False

        # PDF 업로드 (메모리에서 직접)
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=pdf_s3_key,
                Body=pdf_data,
                ContentType='application/pdf'
            )
            logger.info(f"✅ PDF 업로드 성공: {pdf_s3_key}")
            pdf_success = True
        except ClientError as e:
            logger.error(f"❌ PDF 업로드 실패 ({pdf_s3_key}): {e}")
        except Exception as e:
            logger.error(f"❌ PDF 업로드 예상치 못한 오류 ({pdf_s3_key}): {e}")

        # JSON 업로드 (메모리에서 직접)
        try:
            json_data = json.dumps(metadata, ensure_ascii=False, indent=2)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=json_s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"✅ JSON 업로드 성공: {json_s3_key}")
            json_success = True
        except ClientError as e:
            logger.error(f"❌ JSON 업로드 실패 ({json_s3_key}): {e}")
        except Exception as e:
            logger.error(f"❌ JSON 업로드 예상치 못한 오류 ({json_s3_key}): {e}")

        # 결과 로깅
        if pdf_success and json_success:
            logger.info(f"🎉 {rec_idx} 업로드 완료")
        elif pdf_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (PDF만 업로드)")
        elif json_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (JSON만 업로드)")
        else:
            logger.error(f"❌ {rec_idx} 업로드 실패")

        return pdf_success, json_success

    def upload_data_by_deadline(self, pdf_data: bytes, metadata: Dict, rec_idx: str, deadline: str) -> tuple[bool, bool]:
        """
        메모리의 PDF 데이터와 메타데이터를 마감일 기준 경로로 직접 업로드 (로컬 저장 없음)

        Args:
            pdf_data: PDF 바이너리 데이터
            metadata: 메타데이터 딕셔너리
            rec_idx: 채용공고 ID
            deadline: 마감일 (YYYY-MM-DD 형식)

        Returns:
            tuple[bool, bool]: (PDF 업로드 성공 여부, JSON 업로드 성공 여부)
        """
        # S3 경로: datasets/by-deadline/{deadline}/pdf/{rec_idx}.pdf
        pdf_s3_key = f"{S3_PDF_PREFIX}{deadline}/pdf/{rec_idx}.pdf"
        json_s3_key = f"{S3_JSON_PREFIX}{deadline}/json/{rec_idx}.json"

        logger.info(f"📤 메모리에서 직접 업로드: {rec_idx} → {deadline}/")

        pdf_success = False
        json_success = False

        # PDF 업로드 (메모리에서 직접)
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=pdf_s3_key,
                Body=pdf_data,
                ContentType='application/pdf'
            )
            logger.info(f"✅ PDF 업로드 성공: {pdf_s3_key}")
            pdf_success = True
        except ClientError as e:
            logger.error(f"❌ PDF 업로드 실패 ({pdf_s3_key}): {e}")
        except Exception as e:
            logger.error(f"❌ PDF 업로드 예상치 못한 오류 ({pdf_s3_key}): {e}")

        # JSON 업로드 (메모리에서 직접)
        try:
            json_data = json.dumps(metadata, ensure_ascii=False, indent=2)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=json_s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"✅ JSON 업로드 성공: {json_s3_key}")
            json_success = True
        except ClientError as e:
            logger.error(f"❌ JSON 업로드 실패 ({json_s3_key}): {e}")
        except Exception as e:
            logger.error(f"❌ JSON 업로드 예상치 못한 오류 ({json_s3_key}): {e}")

        # 결과 로깅
        if pdf_success and json_success:
            logger.info(f"🎉 {rec_idx} 업로드 완료 (마감일: {deadline})")
        elif pdf_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (PDF만 업로드)")
        elif json_success:
            logger.warning(f"⚠️  {rec_idx} 부분 성공 (JSON만 업로드)")
        else:
            logger.error(f"❌ {rec_idx} 업로드 실패")

        return pdf_success, json_success

    def get_latest_rec_idx(self) -> Optional[str]:
        """
        S3에서 가장 최근 크롤링한 rec_idx 조회

        Returns:
            Optional[str]: latest_rec_idx 또는 None (첫 실행 시)
        """
        try:
            latest_key = f"{S3_METADATA_PREFIX}latest_rec_idx.txt"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=latest_key
            )
            latest_rec_idx = response['Body'].read().decode('utf-8').strip()
            logger.info(f"📌 이전 latest_rec_idx: {latest_rec_idx}")
            return latest_rec_idx
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info("🆕 latest_rec_idx 파일 없음 (첫 실행)")
                return None
            else:
                logger.error(f"❌ latest_rec_idx 조회 오류: {e}")
                raise
        except Exception as e:
            logger.error(f"❌ latest_rec_idx 조회 중 오류: {e}")
            return None

    def save_latest_rec_idx(self, rec_idx: str) -> bool:
        """
        가장 최근 크롤링한 rec_idx를 S3에 저장

        Args:
            rec_idx: 저장할 rec_idx

        Returns:
            bool: 저장 성공 여부
        """
        try:
            latest_key = f"{S3_METADATA_PREFIX}latest_rec_idx.txt"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=latest_key,
                Body=rec_idx.encode('utf-8'),
                ContentType='text/plain'
            )
            logger.info(f"✅ latest_rec_idx 저장: {rec_idx}")
            return True
        except ClientError as e:
            logger.error(f"❌ latest_rec_idx 저장 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ latest_rec_idx 저장 중 오류: {e}")
            return False

    def check_file_exists(self, s3_key: str) -> bool:
        """
        S3에 파일이 존재하는지 확인

        Args:
            s3_key: S3 객체 키

        Returns:
            bool: 파일 존재 여부
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"❌ S3 파일 확인 오류: {e}")
                raise

    def check_rec_idx_exists(self, rec_idx: str) -> tuple[bool, bool]:
        """
        특정 rec_idx의 PDF와 JSON이 S3에 이미 존재하는지 확인

        Args:
            rec_idx: 채용공고 ID

        Returns:
            tuple[bool, bool]: (PDF 존재 여부, JSON 존재 여부)
        """
        pdf_key = f"{S3_PDF_PREFIX}{rec_idx}.pdf"
        json_key = f"{S3_JSON_PREFIX}{rec_idx}.json"

        pdf_exists = self.check_file_exists(pdf_key)
        json_exists = self.check_file_exists(json_key)

        return pdf_exists, json_exists

    def list_all_rec_idx(self) -> list[str]:
        """
        S3에 저장된 모든 rec_idx 목록 조회 (test/initial 모드용)

        Returns:
            list[str]: rec_idx 리스트
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=S3_PDF_PREFIX
            )

            if 'Contents' not in response:
                logger.warning("⚠️  S3에 PDF 파일이 없습니다.")
                return []

            rec_idx_list = []
            for obj in response['Contents']:
                # "initial-dataset/pdf/49421173.pdf" → "49421173"
                filename = Path(obj['Key']).stem
                rec_idx_list.append(filename)

            logger.info(f"✅ S3에서 {len(rec_idx_list)}개의 rec_idx 발견")
            return rec_idx_list

        except Exception as e:
            logger.error(f"❌ S3 목록 조회 실패: {e}")
            return []

    def list_active_rec_ids(self) -> Set[str]:
        """
        마감일이 지나지 않은 활성 공고의 rec_idx 목록 조회 (daily 모드용)

        마감일 >= 오늘인 폴더만 스캔하여 중복 체크 범위를 최적화

        Returns:
            Set[str]: 활성 공고 rec_idx 집합
        """
        try:
            # test/initial 모드는 모든 rec_idx 반환
            if CRAWL_MODE in ['test', 'initial']:
                return set(self.list_all_rec_idx())

            # daily 모드: 마감일 기준 활성 공고만 조회
            today = datetime.now().date()
            active_rec_ids = set()

            logger.info(f"📅 활성 공고 스캔 시작 (마감일 >= {today})...")

            # 1️⃣ 모든 마감일 폴더 조회
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=S3_PDF_PREFIX,  # "datasets/by-deadline/"
                Delimiter='/'
            )

            if 'CommonPrefixes' not in response:
                logger.warning("⚠️  S3에 마감일 폴더가 없습니다.")
                return set()

            # 2️⃣ 각 마감일 폴더 확인
            scanned_folders = 0
            skipped_folders = 0

            for prefix_dict in response.get('CommonPrefixes', []):
                folder_path = prefix_dict['Prefix']  # "datasets/by-deadline/2025-01-31/"
                deadline_str = folder_path.rstrip('/').split('/')[-1]  # "2025-01-31"

                # 날짜 형식 검증
                try:
                    deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                except:
                    logger.warning(f"⚠️  유효하지 않은 날짜 폴더 스킵: {folder_path}")
                    continue

                # 3️⃣ 마감일이 오늘 이후인 폴더만 스캔
                if deadline_date < today:
                    skipped_folders += 1
                    continue

                scanned_folders += 1
                logger.info(f"   📂 스캔 중: {deadline_str}/")

                # 4️⃣ PDF 파일 목록 조회
                pdf_prefix = f"{folder_path}pdf/"
                objs_response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=pdf_prefix
                )

                if 'Contents' in objs_response:
                    for obj in objs_response['Contents']:
                        # "datasets/by-deadline/2025-01-31/pdf/48123456.pdf" → "48123456"
                        rec_idx = Path(obj['Key']).stem
                        active_rec_ids.add(rec_idx)

            logger.info(f"✅ 스캔 완료:")
            logger.info(f"   - 스캔한 폴더: {scanned_folders}개 (마감일 >= {today})")
            logger.info(f"   - 스킵한 폴더: {skipped_folders}개 (마감일 < {today})")
            logger.info(f"   - 활성 공고: {len(active_rec_ids)}개")

            return active_rec_ids

        except Exception as e:
            logger.error(f"❌ 활성 공고 스캔 실패: {e}")
            import traceback
            traceback.print_exc()
            return set()


if __name__ == "__main__":
    # S3 업로더 테스트
    print("\n=== S3 Uploader 테스트 ===\n")

    try:
        uploader = S3Uploader()

        # S3에 저장된 rec_idx 목록 조회
        print("\n📋 S3에 저장된 rec_idx 목록:")
        rec_idx_list = uploader.list_all_rec_idx()
        if rec_idx_list:
            for idx, rec_idx in enumerate(rec_idx_list[:10], 1):
                print(f"   {idx}. {rec_idx}")
            if len(rec_idx_list) > 10:
                print(f"   ... 외 {len(rec_idx_list) - 10}개")

        print("\n✅ S3 Uploader 테스트 완료")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
