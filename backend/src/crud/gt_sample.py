from sqlalchemy.orm import Session
from typing import List, Optional
from db.models import GTSample
from schemas.gt_sample import GTSampleCreate


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