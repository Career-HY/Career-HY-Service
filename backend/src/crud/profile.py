from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import Profile, ClubActivity, JobInterest, CourseCatalog, Certification
from schemas.profile import ProfileCreate, ProfileUpdate


def get_profile(db: Session, member_id: str) -> Profile | None:
    """
    주어진 member_id로 프로필을 조회합니다. 없으면 None을 반환합니다.
    """
    return db.query(Profile).filter(Profile.member_id == member_id).first()


def create_profile(db: Session, member_id: str, data: ProfileCreate) -> Profile:
    """
    로그인된 사용자의 프로필을 생성합니다.
    이미 존재하면 400 에러를 발생시킵니다.
    """
    if get_profile(db, member_id):
        raise HTTPException(status_code=400, detail="이미 프로필이 존재합니다")
    prof = Profile(member_id=member_id, **data.dict())
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def update_profile(db: Session, member_id: str, data: ProfileUpdate) -> Profile:
    """
    로그인된 사용자의 프로필을 수정합니다.
    프로필이 없으면 500 에러를 발생시킵니다. (정상적인 상황에서는 발생하지 않아야 함)
    """
    prof = get_profile(db, member_id)
    if not prof:
        raise HTTPException(status_code=500, detail="프로필이 존재하지 않습니다. 시스템 오류입니다.")
    
    # 기본 프로필 정보 업데이트
    if data.grade is not None:
        prof.grade = data.grade
    if data.department is not None:
        prof.department = data.department
    
    # 동아리 활동 업데이트
    if data.club_activities is not None:
        # 기존 동아리 활동 모두 삭제
        db.query(ClubActivity).filter(ClubActivity.profile_id == member_id).delete()
        
        # 새로운 동아리 활동 추가
        for activity_data in data.club_activities:
            if activity_data.content:  # 내용이 있는 것만 추가
                new_activity = ClubActivity(
                    profile_id=member_id,
                    content=activity_data.content
                )
                db.add(new_activity)
    
    # 관심직무 업데이트
    if data.job_interests is not None:
        # 기존 관심직무 모두 삭제
        db.query(JobInterest).filter(JobInterest.profile_id == member_id).delete()
        
        # 새로운 관심직무 추가
        for interest in data.job_interests:
            if interest.strip():  # 빈 문자열이 아닌 것만 추가
                new_interest = JobInterest(
                    profile_id=member_id,
                    interest=interest.strip()
                )
                db.add(new_interest)
    
    # 자격증 업데이트
    if data.certifications is not None:
        # 기존 자격증 모두 삭제
        db.query(Certification).filter(Certification.member_id == member_id).delete()
        
        # 새로운 자격증 추가
        for cert_data in data.certifications:
            if cert_data.content:  # 내용이 있는 것만 추가
                new_cert = Certification(
                    member_id=member_id,
                    content=cert_data.content,
                    certified_at=cert_data.certified_at
                )
                db.add(new_cert)
    
    # 수강 이력 업데이트 (Many-to-Many 관계)
    if data.course_catalog_ids is not None:
        # 기존 수강 이력 연결 해제
        prof.course_catalogs.clear()
        
        # 새로운 수강 이력 연결
        for catalog_id in data.course_catalog_ids:
            catalog = db.query(CourseCatalog).filter(CourseCatalog.id == catalog_id).first()
            if catalog:
                prof.course_catalogs.append(catalog)
    
    db.commit()
    db.refresh(prof)
    return prof
