from pydantic import BaseModel, Field
from typing import List, Any, Optional
from datetime import datetime

class GTSampleBase(BaseModel):
    seed_rec_idx: str = Field(..., description="기준 채용공고 rec_idx")
    relevant_ids: List[str] = Field(..., description="GT에 포함된 관련 공고 rec_idx 목록")
    profile: dict = Field(..., description="학생 프로필 JSON(CourseInfo 구조 포함)")
    query: str = Field(..., description="학생이 챗봇에 입력할 질문")

class GTSampleCreate(GTSampleBase):
    pass

class GTSampleRead(GTSampleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 