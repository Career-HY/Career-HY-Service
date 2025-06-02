"""
S3에서 데이터를 로드하는 모듈
"""
import os
import json
import boto3
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class S3DataLoader:
    def __init__(self):
        """S3 클라이언트 초기화"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'ap-northeast-2')
            )
            self.bucket_name = 'career-hi'
            logger.info("✅ S3 클라이언트 초기화 완료")
        except NoCredentialsError:
            logger.error("❌ AWS 자격 증명을 찾을 수 없습니다. 환경변수를 확인해주세요.")
            raise
        except Exception as e:
            logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
            raise

    def list_s3_objects(self, prefix: str) -> List[str]:
        """S3에서 특정 prefix의 객체 목록을 가져옵니다."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.warning(f"⚠️ S3에서 {prefix}로 시작하는 객체를 찾을 수 없습니다.")
                return []
                
            objects = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
            logger.info(f"✅ S3에서 {len(objects)}개의 파일을 찾았습니다. (prefix: {prefix})")
            return objects
            
        except ClientError as e:
            logger.error(f"❌ S3 객체 목록 조회 실패: {e}")
            raise

    def download_pdf_files(self) -> List[Path]:
        """S3에서 PDF 파일들을 임시 디렉토리에 다운로드합니다."""
        pdf_prefix = "initial-dataset/pdf/"
        pdf_objects = self.list_s3_objects(pdf_prefix)
        
        pdf_files = [obj for obj in pdf_objects if obj.endswith('.pdf')]
        
        if not pdf_files:
            raise FileNotFoundError(f"❌ S3에서 PDF 파일을 찾을 수 없습니다. (경로: {pdf_prefix})")
        
        # 임시 디렉토리 생성
        temp_dir = Path(tempfile.mkdtemp(prefix="career_hi_pdfs_"))
        downloaded_paths = []
        
        try:
            for pdf_key in pdf_files:
                # 파일명 추출
                filename = Path(pdf_key).name
                local_path = temp_dir / filename
                
                # S3에서 파일 다운로드
                self.s3_client.download_file(
                    self.bucket_name, 
                    pdf_key, 
                    str(local_path)
                )
                downloaded_paths.append(local_path)
                logger.info(f"✅ PDF 다운로드 완료: {filename}")
                
        except Exception as e:
            logger.error(f"❌ PDF 파일 다운로드 실패: {e}")
            # 실패 시 임시 디렉토리 정리
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
            
        logger.info(f"✅ 총 {len(downloaded_paths)}개의 PDF 파일 다운로드 완료")
        return downloaded_paths

    def load_json_files(self) -> List[Dict[Any, Any]]:
        """S3에서 JSON 파일들을 로드합니다."""
        json_prefix = "initial-dataset/json/"
        json_objects = self.list_s3_objects(json_prefix)
        
        json_files = [obj for obj in json_objects if obj.endswith('.json')]
        
        if not json_files:
            raise FileNotFoundError(f"❌ S3에서 JSON 파일을 찾을 수 없습니다. (경로: {json_prefix})")
        
        json_data = []
        
        try:
            for json_key in json_files:
                # S3에서 JSON 파일 읽기
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=json_key
                )
                
                # JSON 내용 파싱
                content = response['Body'].read().decode('utf-8')
                data = json.loads(content)
                
                # 리스트인 경우 확장, 단일 객체인 경우 추가
                if isinstance(data, list):
                    json_data.extend(data)
                else:
                    json_data.append(data)
                    
                logger.info(f"✅ JSON 파일 로드 완료: {Path(json_key).name}")
                
        except Exception as e:
            logger.error(f"❌ JSON 파일 로드 실패: {e}")
            raise
            
        logger.info(f"✅ 총 {len(json_data)}개의 JSON 레코드 로드 완료")
        return json_data

    def cleanup_temp_files(self, file_paths: List[Path]):
        """임시 파일들을 정리합니다."""
        try:
            if file_paths:
                # 임시 디렉토리 정리
                temp_dir = file_paths[0].parent
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ 임시 파일 정리 완료")
        except Exception as e:
            logger.warning(f"⚠️ 임시 파일 정리 중 오류: {e}") 