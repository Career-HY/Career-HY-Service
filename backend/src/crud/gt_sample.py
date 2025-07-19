from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import asyncio
import logging
from db.models import GTSample
from schemas.gt_sample import GTSampleCreate
from util.ingestion_client import IngestionClient

logger = logging.getLogger(__name__)


def create_gt_sample(db: Session, data: GTSampleCreate) -> GTSample:
    # RelevantDoc 객체를 JSON 직렬화 가능한 dict 로 변환
    rel = [item.dict() if hasattr(item, "dict") else item for item in data.relevant_ids]

    sample = GTSample(
        seed_rec_idx=data.seed_rec_idx,
        relevant_ids=rel,
        profile=data.profile,
        query=data.query,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


def get_gt_sample(db: Session, sample_id: int) -> Optional[GTSample]:
    return db.query(GTSample).filter(GTSample.id == sample_id).first()


def list_gt_samples(db: Session, skip: int = 0, limit: int = 200) -> List[GTSample]:
    return db.query(GTSample).offset(skip).limit(limit).all()


async def enrich_all_gt_metadata(db: Session) -> Dict[str, int]:
    """모든 GT 샘플의 메타데이터 수집 및 업데이트"""
    
    all_samples = db.query(GTSample).all()
    logger.info(f"총 {len(all_samples)}개 GT 샘플 발견")
    
    ingestion_client = IngestionClient()
    success_count = 0
    failed_count = 0
    
    for sample in all_samples:
        try:
            relevant_ids = sample.relevant_ids
            docs_metadata = []
            
            for rel_doc in relevant_ids:
                rec_idx = rel_doc.get("rec_idx")
                distance = rel_doc.get("distance", 0.0)
                
                if not rec_idx:
                    continue
                
                posting_data = await ingestion_client.get_posting(rec_idx)
                
                if posting_data:
                    metadata = posting_data.get("metadata", {})
                    excerpt = posting_data.get("excerpt", "")
                    
                    doc_meta = {
                        "rec_idx": rec_idx,
                        "distance": distance,
                        "title": metadata.get("post_title", metadata.get("title", "제목 없음")),
                        "company": metadata.get("company", "회사명 없음"),
                        "deadline": metadata.get("deadline", "마감일 미정"),
                        "url": metadata.get("detail_url", ""),
                        "excerpt": excerpt[:200] if excerpt else "내용 없음"
                    }
                else:
                    doc_meta = {
                        "rec_idx": rec_idx,
                        "distance": distance,
                        "title": "조회 실패",
                        "company": "Unknown",
                        "deadline": "Unknown",
                        "url": "",
                        "excerpt": "메타데이터 조회에 실패했습니다."
                    }
                
                docs_metadata.append(doc_meta)
            
            sample.relevant_docs_metadata = {"docs": docs_metadata}
            success_count += 1
            logger.info(f"GT 샘플 {sample.id} 메타데이터 보강 완료")
            
            await asyncio.sleep(0.3)
            
        except Exception as e:
            failed_count += 1
            logger.error(f"GT 샘플 {sample.id} 처리 실패: {e}")
    
    try:
        db.commit()
        logger.info("모든 메타데이터 업데이트 커밋 완료")
    except Exception as e:
        db.rollback()
        logger.error(f"커밋 실패: {e}")
        raise
    
    return {
        "total": len(all_samples),
        "success": success_count,
        "failed": failed_count
    } 