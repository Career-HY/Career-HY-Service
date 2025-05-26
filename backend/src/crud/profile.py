from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models import Profile
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
    for field, value in data.dict(exclude_unset=True).items():
        setattr(prof, field, value)
    db.commit()
    db.refresh(prof)
    return prof
