from sqlalchemy.orm import Session
from typing import List, Optional
from db.models import GTSample
from schemas.gt_sample import GTSampleCreate


def create_gt_sample(db: Session, data: GTSampleCreate) -> GTSample:
    sample = GTSample(
        seed_rec_idx=data.seed_rec_idx,
        relevant_ids=data.relevant_ids,
        profile=data.profile,
        query=data.query,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


def get_gt_sample(db: Session, sample_id: int) -> Optional[GTSample]:
    return db.query(GTSample).filter(GTSample.id == sample_id).first()


def list_gt_samples(db: Session, skip: int = 0, limit: int = 100) -> List[GTSample]:
    return db.query(GTSample).offset(skip).limit(limit).all() 