"""
S3 데이터를 로드하고 처리하는 통합 서비스
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

from storage import S3DataLoader, store_to_chroma, upsert_to_chroma, query_chroma
from preprocessing import extract_text_PyMuPDF, clean_text
from .embedder import OpenAITextEmbedder

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        """데이터 처리기 초기화"""
        self.s3_loader = S3DataLoader()
        self.embedder = OpenAITextEmbedder()
        # 환경변수를 통한 벡터 저장소 경로 설정
        self.persist_dir = os.getenv(
            "VECTOR_STORE_PATH", 
            "/app/data/vector_store_pymupdf_text-embedding-ada-002_chroma"
        )
        
    def process_s3_data(self) -> Dict[str, Any]:
        """
        S3에서 데이터를 로드하고 벡터 데이터베이스에 저장합니다.
        
        Returns:
            Dict[str, Any]: 처리 결과 요약
        """
        pdf_paths = []
        try:
            logger.info("🚀 S3 데이터 처리 시작...")
            
            # 1. S3에서 PDF 파일 다운로드
            logger.info("📄 S3에서 PDF 파일 다운로드 중...")
            pdf_paths = self.s3_loader.download_pdf_files()
            
            # 2. S3에서 JSON 파일 로드
            logger.info("📊 S3에서 JSON 파일 로드 중...")
            json_data = self.s3_loader.load_json_files()
            
            # 3. JSON 데이터를 딕셔너리로 변환 (파일명 기준 매칭용)
            logger.info("📊 JSON 데이터 인덱싱 중...")
            json_dict = {}
            for item in json_data:
                if isinstance(item, dict) and 'rec_idx' in item:
                    # JSON 파일명에서 rec_idx 추출하여 키로 사용
                    rec_idx = item['rec_idx']
                    json_dict[rec_idx] = item
            
            logger.info(f"📋 {len(json_dict)}개의 JSON 레코드 인덱싱 완료")

            # 4. PDF 텍스트 추출 및 JSON 메타데이터 매칭
            logger.info("🔍 PDF 텍스트 추출 및 JSON 메타데이터 매칭 중...")
            pdf_documents = []
            pdf_metadatas = []
            
            for pdf_path in pdf_paths:
                try:
                    # 텍스트 추출
                    raw_text = extract_text_PyMuPDF(pdf_path)
                    
                    # 텍스트 정리
                    clean_text_result = clean_text(raw_text)
                    
                    if clean_text_result.strip():
                        # PDF 파일명에서 rec_idx 추출 (예: 20250417_49421173.pdf -> 49421173)
                        pdf_filename = pdf_path.stem  # 확장자 제거
                        
                        # 파일명에서 rec_idx 추출 (마지막 '_' 이후 부분)
                        if '_' in pdf_filename:
                            rec_idx = pdf_filename.split('_')[-1]
                        else:
                            rec_idx = pdf_filename
                        
                        # 해당 JSON 메타데이터 찾기
                        json_metadata = json_dict.get(rec_idx)
                        
                        if json_metadata:
                            # JSON 메타데이터와 함께 저장
                            metadata = {
                                "source": "pdf",
                                "filename": pdf_path.name,
                                "document_type": "recruitment_pdf_with_json",
                                "rec_idx": rec_idx
                            }
                            
                            # JSON의 모든 필드를 메타데이터에 추가
                            for key, value in json_metadata.items():
                                if isinstance(value, (str, int, float, bool)):
                                    metadata[key] = str(value)
                            
                            pdf_documents.append(clean_text_result)
                            pdf_metadatas.append(metadata)
                            
                            logger.info(f"✅ PDF {pdf_path.name} + JSON 메타데이터 매칭 완료: {json_metadata.get('post_title', 'Unknown')}")
                        else:
                            # 매칭되는 JSON이 없는 경우 PDF만 저장
                            metadata = {
                                "source": "pdf",
                                "filename": pdf_path.name,
                                "document_type": "recruitment_pdf_only",
                                "rec_idx": rec_idx,
                                "post_title": "제목 없음",
                                "deadline": "미정",
                                "detail_url": ""
                            }
                            
                            pdf_documents.append(clean_text_result)
                            pdf_metadatas.append(metadata)
                            
                            logger.warning(f"⚠️ PDF {pdf_path.name}에 매칭되는 JSON 없음 (rec_idx: {rec_idx})")
                        
                except Exception as e:
                    logger.error(f"❌ PDF 처리 실패 {pdf_path.name}: {e}")
                    continue

            # 5. 벡터 데이터베이스에 저장 (PDF + JSON 매칭 데이터만)
            all_documents = pdf_documents  # JSON 별개 문서 제거
            all_metadatas = pdf_metadatas  # JSON 별개 메타데이터 제거
            
            if all_documents:
                logger.info(f"💾 벡터 데이터베이스에 {len(all_documents)}개 문서 저장 중...")
                
                # 임베딩 생성 (배치 처리)
                logger.info("🔮 임베딩 생성 중...")
                batch_size = 50  # 배치 크기 설정
                all_embeddings = []
                
                for i in range(0, len(all_documents), batch_size):
                    batch_docs = all_documents[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(all_documents) + batch_size - 1) // batch_size
                    
                    logger.info(f"📊 배치 {batch_num}/{total_batches} 처리 중... ({len(batch_docs)}개 문서)")
                    
                    try:
                        batch_embeddings = self.embedder.embed(batch_docs)
                        all_embeddings.extend(batch_embeddings)
                        logger.info(f"✅ 배치 {batch_num}/{total_batches} 완료")
                    except Exception as e:
                        logger.error(f"❌ 배치 {batch_num} 처리 실패: {e}")
                        # 실패한 배치는 건너뛰고 계속 진행
                        # 해당 배치만큼 빈 임베딩으로 채우기 (또는 다른 처리)
                        continue
                
                if len(all_embeddings) != len(all_documents):
                    logger.warning(f"⚠️ 임베딩 개수 불일치: 문서 {len(all_documents)}개, 임베딩 {len(all_embeddings)}개")
                    # 임베딩에 실패한 문서들 제거
                    valid_count = len(all_embeddings)
                    all_documents = all_documents[:valid_count]
                    all_metadatas = all_metadatas[:valid_count]
                
                # 문서 ID 생성
                ids = [f"doc_{i}" for i in range(len(all_documents))]
                
                # Chroma에 저장 (배치 처리)
                logger.info(f"💾 {len(all_documents)}개 문서를 Chroma에 저장 중...")
                chroma_batch_size = 100  # Chroma 저장 배치 크기
                
                for i in range(0, len(all_documents), chroma_batch_size):
                    batch_docs = all_documents[i:i + chroma_batch_size]
                    batch_embeddings = all_embeddings[i:i + chroma_batch_size]
                    batch_ids = ids[i:i + chroma_batch_size]
                    batch_metadatas = all_metadatas[i:i + chroma_batch_size]
                    
                    batch_num = (i // chroma_batch_size) + 1
                    total_batches = (len(all_documents) + chroma_batch_size - 1) // chroma_batch_size
                    
                    logger.info(f"💾 Chroma 저장 배치 {batch_num}/{total_batches} 처리 중...")
                    
                    try:
                        store_to_chroma(
                            texts=batch_docs,
                            embeddings=batch_embeddings,
                            ids=batch_ids,
                            metadatas=batch_metadatas,
                            persist_dir=self.persist_dir
                        )
                        logger.info(f"✅ Chroma 저장 배치 {batch_num}/{total_batches} 완료")
                    except Exception as e:
                        logger.error(f"❌ Chroma 저장 배치 {batch_num} 실패: {e}")
                        # 저장 실패시에도 계속 진행
                        continue
                
                logger.info("✅ 벡터 데이터베이스 저장 완료!")
            else:
                logger.warning("⚠️ 처리할 문서가 없습니다.")
            
            # 처리 결과 요약
            result = {
                "success": True,
                "pdf_files_processed": len(pdf_paths),
                "json_records_processed": len(json_data),
                "total_pdf_documents": len(pdf_documents),
                "total_json_documents": 0,
                "total_documents_stored": len(all_documents)
            }
            
            logger.info(f"🎉 데이터 처리 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 데이터 처리 중 오류 발생: {e}")
            return {
                "success": False,
                "error": str(e),
                "pdf_files_processed": 0,
                "json_records_processed": 0,
                "total_documents_stored": 0
            }
            
        finally:
            # 임시 파일 정리
            if pdf_paths:
                self.s3_loader.cleanup_temp_files(pdf_paths)

    def check_vector_store_status(self) -> Dict[str, Any]:
        """벡터 저장소 상태를 확인합니다."""
        try:
            # 테스트 쿼리로 저장소 상태 확인
            results = query_chroma(
                query="테스트",
                embedder=self.embedder,
                persist_dir=self.persist_dir,
                top_k=1
            )
            
            if results and results.get('documents'):
                document_count = len(results['documents'][0]) if results['documents'][0] else 0
                return {
                    "status": "available",
                    "sample_document_count": document_count,
                    "persist_dir": self.persist_dir
                }
            else:
                return {
                    "status": "empty",
                    "persist_dir": self.persist_dir
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "persist_dir": self.persist_dir
            }

    def process_incremental_data(self, s3_prefix: str, force_update: bool = False) -> Dict[str, Any]:
        """
        S3의 특정 경로에서 데이터를 로드하고 증분 업데이트 (upsert)

        Args:
            s3_prefix (str): S3 경로 (예: "datasets/test/" 또는 "datasets/daily/2025-01-20/")
            force_update (bool): True면 중복 시 덮어쓰기, False면 스킵

        Returns:
            Dict[str, Any]: 처리 결과 요약
        """
        pdf_paths = []
        try:
            logger.info(f"🚀 증분 데이터 처리 시작 (경로: {s3_prefix})")

            # 1. S3에서 PDF 파일 다운로드
            logger.info(f"📄 S3에서 PDF 파일 다운로드 중... (prefix: {s3_prefix}pdf/)")

            # S3DataLoader의 기본 prefix를 임시로 변경
            original_pdf_prefix = "initial-dataset/pdf/"
            original_json_prefix = "initial-dataset/json/"

            # S3 prefix에 맞게 PDF/JSON 다운로드
            pdf_prefix = f"{s3_prefix}pdf/" if not s3_prefix.endswith('/') else f"{s3_prefix}pdf/"
            json_prefix = f"{s3_prefix}json/" if not s3_prefix.endswith('/') else f"{s3_prefix}json/"

            # S3에서 파일 목록 조회
            pdf_objects = self.s3_loader.list_s3_objects(pdf_prefix)
            json_objects = self.s3_loader.list_s3_objects(json_prefix)

            pdf_files = [obj for obj in pdf_objects if obj.endswith('.pdf')]
            json_files = [obj for obj in json_objects if obj.endswith('.json')]

            if not pdf_files:
                logger.warning(f"⚠️  S3 경로에 PDF 파일이 없습니다: {pdf_prefix}")
                return {
                    "success": False,
                    "error": "No PDF files found in S3",
                    "added": 0,
                    "updated": 0,
                    "skipped": 0
                }

            logger.info(f"✅ {len(pdf_files)}개의 PDF 파일 발견")

            # 임시 디렉토리 생성
            from pathlib import Path
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix="career_hi_incremental_"))
            downloaded_pdf_paths = []

            # PDF 다운로드
            for pdf_key in pdf_files:
                filename = Path(pdf_key).name
                local_path = temp_dir / filename

                self.s3_loader.s3_client.download_file(
                    self.s3_loader.bucket_name,
                    pdf_key,
                    str(local_path)
                )
                downloaded_pdf_paths.append(local_path)
                logger.info(f"✅ PDF 다운로드: {filename}")

            pdf_paths = downloaded_pdf_paths

            # 2. S3에서 JSON 파일 로드
            logger.info("📊 S3에서 JSON 파일 로드 중...")
            json_data = []

            for json_key in json_files:
                response = self.s3_loader.s3_client.get_object(
                    Bucket=self.s3_loader.bucket_name,
                    Key=json_key
                )
                content = response['Body'].read().decode('utf-8')
                import json as json_module
                data = json_module.loads(content)

                if isinstance(data, list):
                    json_data.extend(data)
                else:
                    json_data.append(data)

                logger.info(f"✅ JSON 로드: {Path(json_key).name}")

            # 3. JSON 데이터 인덱싱
            json_dict = {}
            for item in json_data:
                if isinstance(item, dict) and 'rec_idx' in item:
                    rec_idx = item['rec_idx']
                    json_dict[rec_idx] = item

            logger.info(f"📋 {len(json_dict)}개의 JSON 레코드 인덱싱 완료")

            # 4. PDF 텍스트 추출 및 JSON 메타데이터 매칭
            logger.info("🔍 PDF 텍스트 추출 및 메타데이터 매칭 중...")
            pdf_documents = []
            pdf_metadatas = []
            pdf_ids = []

            for pdf_path in pdf_paths:
                try:
                    raw_text = extract_text_PyMuPDF(pdf_path)
                    clean_text_result = clean_text(raw_text)

                    if clean_text_result.strip():
                        pdf_filename = pdf_path.stem
                        rec_idx = pdf_filename.split('_')[-1] if '_' in pdf_filename else pdf_filename

                        json_metadata = json_dict.get(rec_idx)

                        metadata = {
                            "source": "pdf",
                            "filename": pdf_path.name,
                            "document_type": "recruitment_pdf_with_json" if json_metadata else "recruitment_pdf_only",
                            "rec_idx": rec_idx
                        }

                        if json_metadata:
                            for key, value in json_metadata.items():
                                if isinstance(value, (str, int, float, bool)):
                                    metadata[key] = str(value)
                            logger.info(f"✅ 매칭 완료: {rec_idx} - {json_metadata.get('post_title', 'Unknown')}")
                        else:
                            metadata.update({
                                "post_title": "제목 없음",
                                "deadline": "미정",
                                "detail_url": ""
                            })
                            logger.warning(f"⚠️  JSON 없음: {rec_idx}")

                        pdf_documents.append(clean_text_result)
                        pdf_metadatas.append(metadata)
                        pdf_ids.append(rec_idx)

                except Exception as e:
                    logger.error(f"❌ PDF 처리 실패 {pdf_path.name}: {e}")
                    continue

            # 5. 임베딩 생성 및 Upsert
            if pdf_documents:
                logger.info(f"💾 {len(pdf_documents)}개 문서 처리 중...")

                # 임베딩 생성
                logger.info("🔮 임베딩 생성 중...")
                batch_size = 50
                all_embeddings = []

                for i in range(0, len(pdf_documents), batch_size):
                    batch_docs = pdf_documents[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(pdf_documents) + batch_size - 1) // batch_size

                    logger.info(f"📊 배치 {batch_num}/{total_batches} 처리 중... ({len(batch_docs)}개 문서)")

                    try:
                        batch_embeddings = self.embedder.embed(batch_docs)
                        all_embeddings.extend(batch_embeddings)
                        logger.info(f"✅ 배치 {batch_num}/{total_batches} 완료")
                    except Exception as e:
                        logger.error(f"❌ 배치 {batch_num} 처리 실패: {e}")
                        continue

                if len(all_embeddings) != len(pdf_documents):
                    logger.warning(f"⚠️  임베딩 개수 불일치: 문서 {len(pdf_documents)}개, 임베딩 {len(all_embeddings)}개")
                    valid_count = len(all_embeddings)
                    pdf_documents = pdf_documents[:valid_count]
                    pdf_metadatas = pdf_metadatas[:valid_count]
                    pdf_ids = pdf_ids[:valid_count]

                # Upsert to ChromaDB (중복 체크)
                logger.info(f"💾 ChromaDB Upsert 중 (force_update={force_update})...")
                upsert_result = upsert_to_chroma(
                    texts=pdf_documents,
                    embeddings=all_embeddings,
                    ids=pdf_ids,
                    metadatas=pdf_metadatas,
                    persist_dir=self.persist_dir,
                    force_update=force_update
                )

                result = {
                    "success": True,
                    "s3_prefix": s3_prefix,
                    "pdf_files_processed": len(pdf_files),
                    "json_records_processed": len(json_data),
                    "added": upsert_result["added"],
                    "updated": upsert_result["updated"],
                    "skipped": upsert_result["skipped"],
                    "total_processed": len(pdf_documents)
                }

                logger.info(f"🎉 증분 데이터 처리 완료: {result}")
                return result

            else:
                logger.warning("⚠️  처리할 문서가 없습니다.")
                return {
                    "success": False,
                    "error": "No documents to process",
                    "added": 0,
                    "updated": 0,
                    "skipped": 0
                }

        except Exception as e:
            logger.error(f"❌ 증분 데이터 처리 중 오류 발생: {e}")
            return {
                "success": False,
                "error": str(e),
                "added": 0,
                "updated": 0,
                "skipped": 0
            }

        finally:
            # 임시 파일 정리
            if pdf_paths:
                self.s3_loader.cleanup_temp_files(pdf_paths) 
    def find_s3_files_by_rec_idx(self, rec_idx: str) -> Dict[str, str]:
        """
        S3에서 특정 rec_idx의 PDF/JSON 파일을 찾습니다 (날짜별 디렉토리 구조)

        Args:
            rec_idx (str): 채용공고 ID

        Returns:
            Dict[str, str]: {"pdf_key": "...", "json_key": "..."} 또는 빈 딕셔너리
        """
        try:
            # S3에서 모든 객체 검색 (날짜별 구조: datasets/{YYYY-MM-DD}/)
            base_prefix = "datasets/"

            logger.info(f"🔍 rec_idx {rec_idx} 파일 검색 중...")

            # S3 전체 스캔 (datasets/ 하위 전체)
            all_objects = self.s3_loader.list_s3_objects(base_prefix)

            pdf_key = None
            json_key = None

            # PDF/JSON 파일 찾기
            for obj_key in all_objects:
                # "datasets/2025-10-21/pdf/52099626.pdf"
                # "datasets/2025-10-21/json/52099626.json"
                if f"/{rec_idx}.pdf" in obj_key:
                    pdf_key = obj_key
                elif f"/{rec_idx}.json" in obj_key:
                    json_key = obj_key

                # 둘 다 찾으면 조기 종료
                if pdf_key and json_key:
                    break

            if pdf_key or json_key:
                logger.info(f"✅ rec_idx {rec_idx} 파일 발견: PDF={bool(pdf_key)}, JSON={bool(json_key)}")
                return {"pdf_key": pdf_key, "json_key": json_key}
            else:
                logger.warning(f"⚠️  rec_idx {rec_idx} 파일을 찾을 수 없습니다")
                return {}

        except Exception as e:
            logger.error(f"❌ rec_idx {rec_idx} 파일 검색 실패: {e}")
            return {}

    def process_by_rec_idx_list(self, rec_idx_list: List[str], force_update: bool = False) -> Dict[str, Any]:
        """
        특정 rec_idx 리스트를 S3에서 찾아 처리합니다 (크롤러 연동용)

        Args:
            rec_idx_list (List[str]): 처리할 rec_idx 리스트
            force_update (bool): True면 중복 시 덮어쓰기, False면 스킵

        Returns:
            Dict[str, Any]: 처리 결과 요약
        """
        pdf_paths = []
        temp_dir = None

        try:
            logger.info(f"🚀 rec_idx 리스트 처리 시작 ({len(rec_idx_list)}개)")

            if not rec_idx_list:
                return {
                    "success": False,
                    "error": "Empty rec_idx_list",
                    "added": 0,
                    "updated": 0,
                    "skipped": 0
                }

            # 임시 디렉토리 생성
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix="career_hi_rec_idx_"))

            downloaded_pdf_paths = []
            json_data_list = []

            # 각 rec_idx에 대해 S3 파일 검색 및 다운로드
            for rec_idx in rec_idx_list:
                logger.info(f"📄 rec_idx {rec_idx} 처리 중...")

                # S3에서 PDF/JSON 파일 찾기
                files = self.find_s3_files_by_rec_idx(rec_idx)

                if not files.get('pdf_key'):
                    logger.warning(f"⚠️  rec_idx {rec_idx}: PDF 없음, 스킵")
                    continue

                # PDF 다운로드
                pdf_key = files['pdf_key']
                filename = Path(pdf_key).name
                local_pdf_path = temp_dir / filename

                self.s3_loader.s3_client.download_file(
                    self.s3_loader.bucket_name,
                    pdf_key,
                    str(local_pdf_path)
                )
                downloaded_pdf_paths.append(local_pdf_path)
                logger.info(f"✅ PDF 다운로드: {filename}")

                # JSON 다운로드 (있으면)
                if files.get('json_key'):
                    json_key = files['json_key']
                    response = self.s3_loader.s3_client.get_object(
                        Bucket=self.s3_loader.bucket_name,
                        Key=json_key
                    )
                    content = response['Body'].read().decode('utf-8')
                    import json as json_module
                    json_data = json_module.loads(content)

                    if isinstance(json_data, list):
                        json_data_list.extend(json_data)
                    else:
                        json_data_list.append(json_data)

                    logger.info(f"✅ JSON 로드: {Path(json_key).name}")

            if not downloaded_pdf_paths:
                logger.warning("⚠️  다운로드된 PDF가 없습니다")
                return {
                    "success": False,
                    "error": "No PDFs found for given rec_idx_list",
                    "added": 0,
                    "updated": 0,
                    "skipped": 0
                }

            pdf_paths = downloaded_pdf_paths

            # JSON 데이터 인덱싱
            json_dict = {}
            for item in json_data_list:
                if isinstance(item, dict) and 'rec_idx' in item:
                    json_dict[item['rec_idx']] = item

            logger.info(f"📋 {len(json_dict)}개의 JSON 레코드 인덱싱 완료")

            # PDF 텍스트 추출 및 JSON 메타데이터 매칭
            logger.info("🔍 PDF 텍스트 추출 및 메타데이터 매칭 중...")
            pdf_documents = []
            pdf_metadatas = []
            pdf_ids = []

            for pdf_path in pdf_paths:
                try:
                    raw_text = extract_text_PyMuPDF(pdf_path)
                    clean_text_result = clean_text(raw_text)

                    if clean_text_result.strip():
                        pdf_filename = pdf_path.stem
                        rec_idx = pdf_filename.split('_')[-1] if '_' in pdf_filename else pdf_filename

                        json_metadata = json_dict.get(rec_idx)

                        metadata = {
                            "source": "pdf",
                            "filename": pdf_path.name,
                            "document_type": "recruitment_pdf_with_json" if json_metadata else "recruitment_pdf_only",
                            "rec_idx": rec_idx
                        }

                        if json_metadata:
                            for key, value in json_metadata.items():
                                if isinstance(value, (str, int, float, bool)):
                                    metadata[key] = str(value)
                            logger.info(f"✅ 매칭 완료: {rec_idx} - {json_metadata.get('post_title', 'Unknown')}")
                        else:
                            metadata.update({
                                "post_title": "제목 없음",
                                "deadline": "미정",
                                "detail_url": ""
                            })
                            logger.warning(f"⚠️  JSON 없음: {rec_idx}")

                        pdf_documents.append(clean_text_result)
                        pdf_metadatas.append(metadata)
                        pdf_ids.append(rec_idx)

                except Exception as e:
                    logger.error(f"❌ PDF 처리 실패 {pdf_path.name}: {e}")
                    continue

            # 임베딩 생성 및 Upsert
            if pdf_documents:
                logger.info(f"💾 {len(pdf_documents)}개 문서 처리 중...")

                # 임베딩 생성
                logger.info("🔮 임베딩 생성 중...")
                batch_size = 50
                all_embeddings = []

                for i in range(0, len(pdf_documents), batch_size):
                    batch_docs = pdf_documents[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(pdf_documents) + batch_size - 1) // batch_size

                    logger.info(f"📊 배치 {batch_num}/{total_batches} 처리 중... ({len(batch_docs)}개 문서)")

                    try:
                        batch_embeddings = self.embedder.embed(batch_docs)
                        all_embeddings.extend(batch_embeddings)
                        logger.info(f"✅ 배치 {batch_num}/{total_batches} 완료")
                    except Exception as e:
                        logger.error(f"❌ 배치 {batch_num} 처리 실패: {e}")
                        continue

                if len(all_embeddings) != len(pdf_documents):
                    logger.warning(f"⚠️  임베딩 개수 불일치: 문서 {len(pdf_documents)}개, 임베딩 {len(all_embeddings)}개")
                    valid_count = len(all_embeddings)
                    pdf_documents = pdf_documents[:valid_count]
                    pdf_metadatas = pdf_metadatas[:valid_count]
                    pdf_ids = pdf_ids[:valid_count]

                # Upsert to ChromaDB
                logger.info(f"💾 ChromaDB Upsert 중 (force_update={force_update})...")
                upsert_result = upsert_to_chroma(
                    texts=pdf_documents,
                    embeddings=all_embeddings,
                    ids=pdf_ids,
                    metadatas=pdf_metadatas,
                    persist_dir=self.persist_dir,
                    force_update=force_update
                )

                result = {
                    "success": True,
                    "rec_idx_list": rec_idx_list,
                    "found_pdfs": len(downloaded_pdf_paths),
                    "added": upsert_result["added"],
                    "updated": upsert_result["updated"],
                    "skipped": upsert_result["skipped"],
                    "total_processed": len(pdf_documents)
                }

                logger.info(f"🎉 rec_idx 리스트 처리 완료: {result}")
                return result

            else:
                logger.warning("⚠️  처리할 문서가 없습니다.")
                return {
                    "success": False,
                    "error": "No documents to process",
                    "added": 0,
                    "updated": 0,
                    "skipped": 0
                }

        except Exception as e:
            logger.error(f"❌ rec_idx 리스트 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "added": 0,
                "updated": 0,
                "skipped": 0
            }

        finally:
            # 임시 파일 정리
            if pdf_paths:
                self.s3_loader.cleanup_temp_files(pdf_paths)
