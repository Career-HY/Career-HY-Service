# 스키마 정의

from pydantic import BaseModel  # json 형식으로 변환
from typing import List, Optional


class CourseInfo(BaseModel):
    course_name: str
    core_competency: str
    course_overview: str
    course_objectives: str
    week1_plan: str
    week2_plan: str
    week3_plan: str
    week4_plan: str
    week5_plan: str
    week6_plan: str
    week7_plan: str
    week8_plan: str
    week9_plan: str
    week10_plan: str
    week11_plan: str
    week12_plan: str
    week13_plan: str
    week14_plan: str
    week15_plan: str
    week16_plan: str


class JobPosting(BaseModel):
    """채용공고 정보"""

    rec_idx: Optional[str] = None           # 공고 ID
    title: str
    url: str
    deadline: Optional[str] = None
    start_date: Optional[str] = None        # 모집 시작일
    crawling_time: Optional[str] = None     # 크롤링 시간
    content: str
    similarity_score: Optional[float] = None  # 유사도 점수 추가


class RetrievalRequest(BaseModel):
    """사용자 프로필 기반 검색 요청"""

    major: str
    catalogs: List[CourseInfo]
    interest_job: List[str]
    certification: List[str]
    club_activities: List[str] = [] 
    query: Optional[str] = None


class RetrievalResponse(BaseModel):
    """검색 결과 응답"""

    results: List[JobPosting]


class VectorSearchRequest(BaseModel):
    """벡터 검색 테스트 요청"""
    
    query: str
    top_k: Optional[int] = 5  # 기본값 5개


class VectorSearchResponse(BaseModel):
    """벡터 검색 테스트 응답"""

    query: str
    total_found: int
    results: List[JobPosting]
    search_time_ms: Optional[float] = None  # 검색 소요 시간 (밀리초)


class IncrementalDataRequest(BaseModel):
    """증분 데이터 처리 요청"""

    s3_prefix: Optional[str] = None         # S3 경로 (예: "datasets/test/" 또는 "datasets/daily/2025-01-20/")
    rec_idx_list: Optional[List[str]] = None  # 특정 rec_idx 리스트 (크롤러에서 전달)
    force_update: bool = False              # True면 중복 시 덮어쓰기, False면 스킵


class IncrementalDataResponse(BaseModel):
    """증분 데이터 처리 응답"""

    success: bool
    s3_prefix: Optional[str] = None
    added: int                              # 신규 추가 개수
    updated: int                            # 업데이트 개수
    skipped: int                            # 스킵 개수
    total_processed: int                    # 총 처리 개수
    error: Optional[str] = None
