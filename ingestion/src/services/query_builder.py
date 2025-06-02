"""
사용자 프로필 기반 검색 쿼리 생성 모듈
"""
from typing import List, Dict, Any


class ProfileQueryBuilder:
    """사용자 프로필 정보를 기반으로 검색 쿼리를 생성하는 클래스"""
    
    @staticmethod
    def create_profile_query(
        major: str, 
        catalogs: List[Dict[str, Any]], 
        interest_job: List[str], 
        certification: List[str]
    ) -> str:
        """
        사용자 프로필 기반 검색 쿼리 생성
        
        Args:
            major: 전공
            catalogs: 강의 목록
            interest_job: 관심 직무 목록  
            certification: 자격증 목록
            
        Returns:
            str: 생성된 검색 쿼리
        """
        query_parts = []

        # 전공 정보 추가
        if major:
            query_parts.append(f"전공: {major}")

        # 관심 직무 추가
        if interest_job:
            query_parts.append(f"관심 직무: {', '.join(interest_job)}")

        # 자격증 정보 추가
        if certification:
            query_parts.append(f"자격증: {', '.join(certification)}")

        # 강의 정보에서 핵심 키워드 추출
        course_keywords = set()
        for course in catalogs:
            # 강의명과 핵심역량에서 키워드 추출
            course_keywords.update(course.course_name.split())
            course_keywords.update(course.core_competency.split())

        if course_keywords:
            query_parts.append(f"관련 키워드: {' '.join(course_keywords)}")
        
        return " ".join(query_parts) 