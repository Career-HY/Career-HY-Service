from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.profile import ProfileRead
from crud.profile import get_profile
from db.session import get_db
from util.deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("", response_model=ProfileRead)
def read_own_profile(
    current_user = Depends(get_current_user),  # 로그인 확인: 로그인이 안되어있으면 401 에러 발생
    db: Session = Depends(get_db),
):
    """
    현재 로그인한 사용자의 프로필을 조회합니다.
    
    - 로그인이 되어있지 않으면 401 Unauthorized 에러가 발생합니다.
    - 로그인은 되어있지만 프로필이 없으면 404 Not Found 에러가 발생합니다.
    """
    # 프로필 조회
    profile = get_profile(db, current_user.id)
    
    # 프로필이 없으면 404 에러 발생
    if not profile:
        raise HTTPException(
            status_code=404, 
            detail="프로필이 존재하지 않습니다. 프로필을 먼저 생성해주세요."
        )
    
    return profile
