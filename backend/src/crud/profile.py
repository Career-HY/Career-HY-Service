from sqlalchemy.orm import Session
from db.models import Profile

def get_profile(db: Session, member_id: str) -> Profile | None:
    """
    member_id 에 해당하는 Profile 객체를 반환.
    없으면 None.
    """
    return db.query(Profile).filter(Profile.member_id == member_id).first()
