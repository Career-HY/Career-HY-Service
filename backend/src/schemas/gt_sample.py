from pydantic import BaseModel, Field
from typing import List, Any, Optional, Dict
from datetime import datetime

class RelevantDoc(BaseModel):
    rec_idx: str = Field(..., description="관련 공고 rec_idx")
    distance: float = Field(..., description="시드 문서와의 거리")

class GTSampleBase(BaseModel):
    seed_rec_idx: str = Field(..., description="기준 채용공고 rec_idx")
    relevant_ids: List[RelevantDoc] = Field(..., description="시드 포함 관련 공고 리스트(거리 포함)")
    profile: dict = Field(..., description="학생 프로필 JSON(CourseInfo 구조 포함)")
    query: str = Field(..., description="학생이 챗봇에 입력할 질문")
    relevant_docs_metadata: Optional[Dict[str, Any]] = Field(None, description="관련 문서 메타데이터")

class GTSampleCreate(GTSampleBase):
    pass

class GTSampleRead(GTSampleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 