from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """채팅 요청 스키마"""
    message: str = Field(..., description="사용자 메시지")


class RecommendedJob(BaseModel):
    """추천된 채용공고"""
    rec_idx: Optional[str] = None  
    title: str
    url: str
    deadline: Optional[str] = None
    start_date: Optional[str] = None  
    crawling_time: Optional[str] = None  
    recommendation_reason: str


class ChatResponse(BaseModel):
    """채팅 응답 스키마"""
    user_message: str = Field(..., description="사용자가 보낸 메시지")
    llm_response: str = Field(..., description="LLM 응답 내용")
    recommended_jobs: List[RecommendedJob] = Field(default=[], description="추천된 채용 공고 목록")
    created_at: datetime = Field(..., description="응답 생성 시간")


class LLMServiceRequest(BaseModel):
    """LLM 서비스로 보낼 요청 스키마"""
    query: str = Field(..., description="사용자 질문")
    profile: dict = Field(..., description="사용자 프로필")


class LLMServiceResponse(BaseModel):
    """LLM 서비스로부터 받을 응답 스키마"""
    content: str
    recommended_jobs: List[RecommendedJob] = Field(default=[], description="추천된 채용 공고 목록") 