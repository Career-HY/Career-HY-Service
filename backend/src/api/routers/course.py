from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from schemas.course import CourseCatalogSearch, CourseCatalogSearchResult
from crud.course import search_courses
from db.session import get_db
from util.logging import log_api_call

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/search", response_model=List[CourseCatalogSearchResult])
@log_api_call
def search_course_catalog(
    q: Optional[str] = Query(None, description="검색어 (과목명 또는 개설학과에서 검색)"),
    limit: int = Query(50, description="검색 결과 개수 제한", le=100),
    offset: int = Query(0, description="검색 결과 시작 위치"),
    db: Session = Depends(get_db)
):
    """
    수강편람에서 과목을 검색합니다.
    
    - **q**: 검색어 (과목명과 개설학과에서 동시에 검색)
    - **limit**: 최대 검색 결과 개수 (기본 50개, 최대 100개)
    - **offset**: 페이징을 위한 시작 위치
    
    검색어가 과목명 또는 개설학과에 포함되어 있으면 결과에 포함됩니다.
    예: '인공'으로 검색하면 '인공지능과 이해' 과목과 '인공지능학과' 개설 과목이 모두 검색됩니다.
    """
    
    search_params = CourseCatalogSearch(
        q=q,
        limit=limit,
        offset=offset
    )
    
    return search_courses(db, search_params) 