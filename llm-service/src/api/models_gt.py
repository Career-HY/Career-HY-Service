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