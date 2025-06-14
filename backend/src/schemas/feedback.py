from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobRecommendationFeedbackCreate(BaseModel):
    chat_history_id: int = Field(..., description="평가 대상 chat_history PK")
    rating: int = Field(..., ge=1, le=5, description="별점(1~5)")
    reason: Optional[str] = Field(None, description="별점 이유")

class JobRecommendationFeedbackRead(BaseModel):
    id: int
    chat_history_id: int
    member_id: str
    rating: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True 