from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.profile import ProfileRead
from crud.profile import get_profile
from db.session import get_db
from api.deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/", response_model=ProfileRead)
def read_own_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prof = get_profile(db, current_user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="프로필이 없습니다")
    return prof
