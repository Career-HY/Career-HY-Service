from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from schemas.profile import ProfileRead
from db.models import CourseCatalog
from util.logging import log_db_operation
import logging

logger = logging.getLogger(__name__)


def convert_profile_to_llm_format(profile: ProfileRead, db: Session) -> Dict[str, Any]:
    """
    백엔드 프로필을 LLM-service 요청 형식으로 변환합니다.
    
    Args:
        profile: 백엔드 프로필 데이터
        db: SQLAlchemy 세션
        
    Returns:
        Dict: LLM-service RetrievalRequest 형식의 딕셔너리
    """
    try:
        # 1. major: department를 major로 매핑
        major = profile.department or "미지정"
        
        # 2. catalogs: course_catalogs를 CourseInfo 형식으로 변환
        catalogs = _convert_course_catalogs(profile.course_catalogs, db)
        
        # 3. interest_job: job_interests를 문자열 리스트로 변환
        interest_job = [job.interest for job in profile.job_interests]
        
        # 4. certification: certifications를 문자열 리스트로 변환
        certification = [cert.content for cert in profile.certifications if cert.content]
        
        result = {
            "major": major,
            "catalogs": catalogs,
            "interest_job": interest_job,
            "certification": certification
        }
        
        logger.info(f"프로필 변환 완료: 전공={major}, 과목수={len(catalogs)}, 관심직무수={len(interest_job)}, 자격증수={len(certification)}")
        return result
        
    except Exception as e:
        logger.error(f"프로필 변환 중 오류 발생: {str(e)}")
        raise Exception("프로필 데이터 변환 중 오류가 발생했습니다.")


@log_db_operation("SELECT")
def _convert_course_catalogs(course_catalogs: List, db: Session) -> List[Dict[str, Any]]:
    """
    수강 과목 목록을 CourseInfo 형식으로 변환합니다.
    
    Args:
        course_catalogs: 백엔드 CourseCatalogRead 리스트
        db: SQLAlchemy 세션
        
    Returns:
        List[Dict]: CourseInfo 형식의 딕셔너리 리스트
    """
    result = []
    
    for course_catalog in course_catalogs:
        try:
            # DB에서 상세 Course 정보 조회
            course_detail = db.query(CourseCatalog).filter(
                CourseCatalog.id == course_catalog.id
            ).first()
            
            if course_detail:
                course_info = _create_course_info_dict(course_detail)
                result.append(course_info)
            else:
                logger.warning(f"Course ID {course_catalog.id}에 대한 상세 정보를 찾을 수 없습니다.")
                
        except Exception as e:
            logger.error(f"Course ID {course_catalog.id} 변환 중 오류: {str(e)}")
            continue
    
    return result


def _create_course_info_dict(course: CourseCatalog) -> Dict[str, Any]:
    """
    CourseCatalog 모델을 CourseInfo 딕셔너리로 변환합니다.
    
    Args:
        course: CourseCatalog 모델 인스턴스
        
    Returns:
        Dict: CourseInfo 형식의 딕셔너리
    """
    return {
        "course_name": course.course_name or "",
        "core_competency": course.core_competency or "",
        "course_overview": course.course_overview or "",
        "course_objectives": course.course_objectives or "",
        "week1_plan": course.week1_plan or "",
        "week2_plan": course.week2_plan or "",
        "week3_plan": course.week3_plan or "",
        "week4_plan": course.week4_plan or "",
        "week5_plan": course.week5_plan or "",
        "week6_plan": course.week6_plan or "",
        "week7_plan": course.week7_plan or "",
        "week8_plan": course.week8_plan or "",
        "week9_plan": course.week9_plan or "",
        "week10_plan": course.week10_plan or "",
        "week11_plan": course.week11_plan or "",
        "week12_plan": course.week12_plan or "",
        "week13_plan": course.week13_plan or "",
        "week14_plan": course.week14_plan or "",
        "week15_plan": course.week15_plan or "",
        "week16_plan": course.week16_plan or "",
    } 