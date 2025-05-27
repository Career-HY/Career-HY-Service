from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.profile import (
    ProfileRead,
    ProfileUpdate
)
from crud.profile import (
    get_profile,
    update_profile
)
from db.session import get_db
from util.deps import get_current_user
from util.logging import log_api_call

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("", response_model=ProfileRead)
@log_api_call
def read_own_profile(
    current_user = Depends(get_current_user),  # 로그인 확인: 로그인이 안되어있으면 401 에러 발생
    db: Session = Depends(get_db),
):
    """
    현재 로그인한 사용자의 프로필을 조회합니다.
    
    - 로그인이 되어있지 않으면 401 Unauthorized 에러가 발생합니다.
    - 회원가입 시 자동으로 빈 프로필이 생성되므로 항상 프로필이 존재합니다.
    """
    # 프로필 조회
    profile = get_profile(db, current_user.id)
    
    # 프로필이 없으면 500 에러 발생 (정상적인 상황에서는 발생하지 않아야 함)
    if not profile:
        raise HTTPException(
            status_code=500, 
            detail="프로필이 존재하지 않습니다. 시스템 오류입니다."
        )
    
    return profile

@router.patch(
    "",
    response_model=ProfileRead
)
@log_api_call
def edit_profile(
    data: ProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session  = Depends(get_db),
):
    """
    현재 로그인한 사용자의 프로필을 수정합니다.

    - 프로필이 없으면 500 Internal Server Error를 반환합니다. (정상적인 상황에서는 발생하지 않아야 함)
    """
    return update_profile(db, current_user.id, data)