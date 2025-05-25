from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserRead, UserLogin
from crud.user import create_user, get_user_by_email, authenticate_user
from db.session import get_db

router = APIRouter()


@router.post("/signup", response_model=UserRead, status_code=201)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1) 이메일 중복 체크
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=400,
            detail="이미 사용 중인 이메일입니다."
        )

    # 2) 신규 사용자 생성
    user = create_user(db, user_in)

    # 3) 생성된 UserRead 모델 반환
    return user


@router.post("/login", response_model=UserRead)
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
