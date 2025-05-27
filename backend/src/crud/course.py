from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from db.models import CourseCatalog
from schemas.course import CourseCatalogSearch

def search_courses(db: Session, search_params: CourseCatalogSearch) -> List[CourseCatalog]:
    """
    수강편람에서 과목을 검색합니다.
    검색어가 과목명 또는 개설학과에 포함되어 있으면 결과에 포함됩니다.
    """
    query = db.query(CourseCatalog)
    
    # 검색어가 있는 경우 과목명과 개설학과에서 동시에 검색
    if search_params.q:
        search_term = f"%{search_params.q}%"
        query = query.filter(
            or_(
                CourseCatalog.course_name.like(search_term),
                CourseCatalog.offering_department.like(search_term)
            )
        )
    
    # 정렬 (과목명 순)
    query = query.order_by(CourseCatalog.course_name, CourseCatalog.academic_year.desc())
    
    # 페이징
    query = query.offset(search_params.offset).limit(search_params.limit)
    
    return query.all() 