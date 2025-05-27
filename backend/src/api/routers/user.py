from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserRead, UserLogin
from crud.user import create_user, get_user_by_email, authenticate_user
from db.session import get_db
from util.logging import log_api_call

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserRead, status_code=201)
@log_api_call
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    신규 사용자를 생성합니다.
    이메일 중복 검사와 프로필 생성은 create_user()에서 처리됩니다.
    """
    # 신규 사용자 생성 (중복 검사 포함)
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=UserRead)
@log_api_call
def login(
    creds: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    
    user = authenticate_user(db, creds)
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    
    request.session["user_id"] = user.id
    return user
