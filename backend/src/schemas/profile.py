from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ClubActivityRead(BaseModel):
    id: int
    content: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class JobInterestRead(BaseModel):
    interest: str
    
    model_config = ConfigDict(from_attributes=True)

class CertificationRead(BaseModel):
    id: int
    content: Optional[str]
    certified_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class CourseCatalogRead(BaseModel):
    id: int
    
    course_name: Optional[str]
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