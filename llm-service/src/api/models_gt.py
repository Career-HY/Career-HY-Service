from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class GTGenerateRequest(BaseModel):
    seed_rec_idx: Optional[str] = Field(None, description="기준 채용공고 rec_idx. 없으면 랜덤")
    num_similar: int = Field(4, ge=1, le=5, description="시드 외에 선택할 문서 수 (1~5)")


class GeneratedGTSample(BaseModel):
    seed_rec_idx: str
    relevant_ids: List[Dict[str, Any]]  # {rec_idx, distance}
    profile: Dict[str, Any]
    query: str 


class GTBatchGenerateRequest(BaseModel):
    """배치 GT 생성 요청 모델"""
    count: int = Field(100, ge=1, le=200, description="생성할 샘플 개수 (1~200)")
    num_similar: int = Field(4, ge=1, le=5, description="각 샘플에 포함할 유사 문서 수 (1~5)")


class GTBatchGenerateResponse(BaseModel):
    """배치 GT 생성 응답 모델"""
    generated: int = Field(..., description="성공적으로 생성·저장된 샘플 개수")
    failed: int = Field(..., description="실패한 샘플 개수")
    ids: List[int] = Field(..., description="백엔드에 저장된 GT 샘플 ID 목록 (성공 건) ")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="실패한 항목의 인덱스 및 상세 오류 메시지 목록"
    ) 