from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

class CourseCatalogSearch(BaseModel):
    """수강편람 검색 파라미터"""
    q: Optional[str] = None  # 과목명과 개설학과로 검색
    limit: int = 50
    offset: int = 0

class CourseCatalogSearchResult(BaseModel):
    """수강편람 검색 결과 (상세 정보 포함)"""
    id: int
    academic_year: Optional[int] = None
    section: Optional[int] = None
    credit_type: Optional[str] = None
    credit_units: Optional[str] = None
    domain: Optional[str] = None
    course_number: Optional[str] = None
    course_code: Optional[str] = None
    old_course_name: Optional[str] = None
    course_name: Optional[str] = None
    course_guide: Optional[str] = None
    accreditation_type: Optional[str] = None
    degree_program: Optional[str] = None
    instructor: Optional[str] = None
    total_credits: Optional[Decimal] = None
    lecture_credits: Optional[Decimal] = None
    lab_credits: Optional[Decimal] = None
    course_category: Optional[str] = None
    enrollment_capacity: Optional[str] = None
    class_format: Optional[str] = None
    class_time: Optional[str] = None
    classroom: Optional[str] = None
    completion_restriction: Optional[str] = None
    detailed_info: Optional[str] = None
    core_competency: Optional[str] = None
    offering_department: Optional[str] = None
    course_overview: Optional[str] = None
    course_objectives: Optional[str] = None
    week1_plan: Optional[str] = None
    week2_plan: Optional[str] = None
    week3_plan: Optional[str] = None
    week4_plan: Optional[str] = None
    week5_plan: Optional[str] = None
    week6_plan: Optional[str] = None
    week7_plan: Optional[str] = None
    week8_plan: Optional[str] = None
    week9_plan: Optional[str] = None
    week10_plan: Optional[str] = None
    week11_plan: Optional[str] = None
    week12_plan: Optional[str] = None
    week13_plan: Optional[str] = None
    week14_plan: Optional[str] = None
    week15_plan: Optional[str] = None
    week16_plan: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) 