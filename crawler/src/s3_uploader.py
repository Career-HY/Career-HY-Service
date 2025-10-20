"""
S3 업로드 모듈

PDF 및 JSON 파일을 AWS S3에 업로드
"""
import os
import boto3
from pathlib import Path
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
import logging

from .config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_DEFAULT_REGION,
    S3_BUCKET_NAME,
    S3_PDF_PREFIX,
    S3_JSON_PREFIX
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
        PDF와 JSON을 함께 업로드

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
        S3에 저장된 모든 rec_idx 목록 조회

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
