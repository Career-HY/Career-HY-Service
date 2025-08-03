"""
사용자 프로필 기반 검색 쿼리 생성 모듈
"""
from typing import List, Dict, Any, Optional
from api.models import CourseInfo 


class ProfileQueryBuilder:
    """사용자 프로필 정보를 기반으로 검색 쿼리를 생성하는 클래스"""
    
    @staticmethod
    def create_profile_query(
        major: str, 
        catalogs: List[CourseInfo],  
        interest_job: List[str], 
        certification: List[str],
        club_activities: Optional[List[str]] = None, 
        query: Optional[str] = None  
    ) -> str:
        """
        사용자 프로필 기반 검색 쿼리 생성
        
        Args:
            major: 전공
            catalogs: 강의 목록 (CourseInfo 객체 리스트)
            interest_job: 관심 직무 목록  
            certification: 자격증 목록
            club_activities: 동아리/대외활동 목록 
            query: 사용자 질문 
            
        Returns:
            str: 생성된 검색 쿼리
        """
        query_parts = []

        # 사용자 질문
        if query:
            query_parts.append(f"질문: {query}")

        # 전공 정보
        if major:
            query_parts.append(f"전공: {major}")

        # 관심 직무
        if interest_job:
            query_parts.append(f"관심 직무: {', '.join(interest_job)}")

        # 자격증 정보
        if certification:
            query_parts.append(f"자격증: {', '.join(certification)}")

        # 동아리/대외활동 정보
        if club_activities:
            query_parts.append(f"동아리/대외활동: {', '.join(club_activities)}")

        # 강의 정보 전체
        if catalogs:
            query_parts.append("수강 이력:")
            for course in catalogs:
                # 각 강의의 모든 정보를 구조화하여 추가
                course_parts = []
                course_parts.append(f"강의명: {course.course_name}")
                course_parts.append(f"핵심 역량: {course.core_competency}")
                course_parts.append(f"강의 개요: {course.course_overview}")
                course_parts.append(f"학습 목표: {course.course_objectives}")
                
                # 주차별 계획 추가
                week_plans = []
                for i in range(1, 17):  # 1주차부터 16주차까지
                    week_plan = getattr(course, f'week{i}_plan')
                    week_plans.append(f"{i}주차: {week_plan}")
                
                course_parts.append(f"주차별 계획: {' / '.join(week_plans)}")
                
                # 강의 정보들을 구분자로 구분하여 추가
                query_parts.append(" | ".join(course_parts))
        
        # 모든 부분을 줄바꿈으로 구분하여 하나의 문자열로 결합
        return "\n".join(query_parts) 