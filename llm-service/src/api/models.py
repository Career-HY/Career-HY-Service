from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CourseInfo(BaseModel):
    course_name: str
    core_competency: Optional[str] = ""
    course_overview: Optional[str] = ""
    course_objectives: Optional[str] = ""
    week1_plan: Optional[str] = ""
    week2_plan: Optional[str] = ""
    week3_plan: Optional[str] = ""
    week4_plan: Optional[str] = ""
    week5_plan: Optional[str] = ""
    week6_plan: Optional[str] = ""
    week7_plan: Optional[str] = ""
    week8_plan: Optional[str] = ""
    week9_plan: Optional[str] = ""
    week10_plan: Optional[str] = ""
    week11_plan: Optional[str] = ""
    week12_plan: Optional[str] = ""
    week13_plan: Optional[str] = ""
    week14_plan: Optional[str] = ""
    week15_plan: Optional[str] = ""
    week16_plan: Optional[str] = ""


class JobPosting(BaseModel):
    """채용공고 정보"""

    rec_idx: Optional[str] = None  # 공고 ID
    title: str
    url: str
    deadline: Optional[str] = None
    start_date: Optional[str] = None  # 모집 시작일
    crawling_time: Optional[str] = None  # 크롤링 시간
    content: str


class RetrievalRequest(BaseModel):
    """사용자 프로필 기반 검색 요청"""

    major: str
    catalogs: List[CourseInfo]
    interest_job: List[str]
    certification: List[str]
    club_activities: List[str] = []
    query: Optional[str] = None
    filter_expired: Optional[bool] = True  # 마감 지난 공고 필터링 (기본값: True) 


class ChatHistoryMessage(BaseModel):
    role: str = Field(..., description="메시지 발신자: user 또는 llm")
    content: str = Field(..., description="메시지 내용")
    recommended_jobs: Optional[List[Dict[str, Any]]] = None  # 추천 채용공고(선택)


class LLMRequest(BaseModel):
    """LLM 서비스 요청"""

    query: str = Field(..., description="사용자 질문")
    profile: RetrievalRequest = Field(..., description="사용자 프로필")
    chat_history: Optional[List[Dict[str, Any]]] = None  # 대화 이력 (유연하게 허용)


class RecommendedJob(BaseModel):
    """추천된 채용공고"""
    
    rec_idx: Optional[str] = None  
    title: str
    url: str
    deadline: Optional[str] = None
    start_date: Optional[str] = None  
    crawling_time: Optional[str] = None  
    recommendation_reason: str


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    recommended_jobs: Optional[List[RecommendedJob]] = None


class LLMRequest(BaseModel):
    """LLM 서비스 요청"""

    query: str = Field(..., description="사용자 질문")
    profile: RetrievalRequest = Field(..., description="사용자 프로필")
    chat_history: Optional[List[ChatHistoryMessage]] = None 


class LLMResponse(BaseModel):
    """LLM 서비스 응답"""

    content: str
    recommended_jobs: List[RecommendedJob] = Field(
        ..., description="추천된 채용 공고 목록"
    )
