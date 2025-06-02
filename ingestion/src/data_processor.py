"""
S3 데이터를 로드하고 처리하는 통합 서비스
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

from s3_loader import S3DataLoader
from loader import extract_text_PyMuPDF
from cleaner import clean_text
from embedder import OpenAITextEmbedder
from vector import store_to_chroma

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
            from vector import query_chroma
            
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