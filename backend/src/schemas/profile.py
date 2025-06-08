from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ClubActivityRead(BaseModel):
    id: int
    content: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ClubActivityCreate(BaseModel):
    content: Optional[str] = None

class ClubActivityUpdate(BaseModel):
    id: Optional[int] = None  # 수정할 때는 ID 필요
    content: Optional[str] = None

class JobInterestRead(BaseModel):
    interest: str
    
    model_config = ConfigDict(from_attributes=True)

class JobInterestCreate(BaseModel):
    interest: str

class CertificationRead(BaseModel):
    id: int
    content: Optional[str]
    certified_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class CertificationCreate(BaseModel):
    content: Optional[str] = None
    certified_at: Optional[datetime] = None

class CertificationUpdate(BaseModel):
    id: Optional[int] = None  # 수정할 때는 ID 필요
    content: Optional[str] = None
    certified_at: Optional[datetime] = None

class CourseCatalogRead(BaseModel):
    id: int
    course_name: Optional[str]
    course_code: Optional[str]
    credit_units: Optional[str]
    instructor: Optional[str]
    offering_department: Optional[str]
    total_credits: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)

class ProfileRead(BaseModel):
    member_id:       str
    grade:           Optional[str] = None
    department:      Optional[str] = None

    club_activities: List[ClubActivityRead]   = []
    job_interests:   List[JobInterestRead]     = []
    certifications:  List[CertificationRead]   = []
    course_catalogs: List[CourseCatalogRead]   = []

    model_config = ConfigDict(from_attributes=True)

class ProfileCreate(BaseModel):
    grade:      Optional[str] = None
    department: Optional[str] = None

class ProfileUpdate(BaseModel):
    grade:           Optional[str] = None
    department:      Optional[str] = None
    club_activities: Optional[List[ClubActivityUpdate]] = None
    job_interests:   Optional[List[str]] = None  # 관심직무는 문자열 리스트로 간단하게
    certifications:  Optional[List[CertificationUpdate]] = None
    course_catalog_ids: Optional[List[int]] = None  # 수강 이력은 기존 카탈로그 ID 리스트