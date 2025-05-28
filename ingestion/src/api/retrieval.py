from pydantic import BaseModel
from typing import List

#스키마 정의 
class Catalog(BaseModel): 
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

class RetrievalRequest(BaseModel): 
    query: str # 사용자의 쿼리
    major: str # 사용자 전공 
    catalogs: List[Catalog] # 수강 이력 
    interest_job: List[str] # 관심 직업 
    certification: List[str] # 자격증 
    
class RetrievalResponse(BaseModel): 
    docs: List[str] # 검색 결과 
    
    
    