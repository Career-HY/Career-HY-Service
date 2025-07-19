from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from schemas.gt_sample import GTSampleCreate, GTSampleRead
from crud.gt_sample import create_gt_sample, get_gt_sample, list_gt_samples, enrich_all_gt_metadata
from db.session import get_db
import os

router = APIRouter(prefix="/gt-samples", tags=["gt-samples"])

# 간단한 API Key 인증 (헤더: X-API-Key)
API_KEYS = [k.strip() for k in os.getenv("ADMIN_API_KEYS", "").split(",") if k.strip()]

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not API_KEYS:
        # 키가 설정되지 않은 경우 인증 스킵 (개발용)
        return True
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True


@router.post("", response_model=GTSampleRead, status_code=201)
def create_sample(data: GTSampleCreate, _: bool = Depends(verify_api_key), db: Session = Depends(get_db)):
    sample = create_gt_sample(db, data)
    return sample


@router.get("/{sample_id}", response_model=GTSampleRead)
def read_sample(sample_id: int, _: bool = Depends(verify_api_key), db: Session = Depends(get_db)):
    sample = get_gt_sample(db, sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.get("", response_model=List[GTSampleRead])
def list_samples(skip: int = 0, limit: int = 100, _: bool = Depends(verify_api_key), db: Session = Depends(get_db)):
    return list_gt_samples(db, skip, limit)


@router.post("/enrich-all-metadata")
async def enrich_all_gt_metadata_endpoint(
    _: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """모든 GT 샘플의 메타데이터 보강"""
    
    try:
        result = await enrich_all_gt_metadata(db)
        
        return {
            "message": "모든 GT 샘플 메타데이터 보강 완료",
            "total_samples": result["total"],
            "success_count": result["success"], 
            "failed_count": result["failed"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"메타데이터 보강 중 오류 발생: {str(e)}"
        ) 