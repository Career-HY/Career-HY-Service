from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserRead
from crud.user import create_user, get_user_by_email
from db.session import get_db

router = APIRouter(prefix="/users", tags=["users"])


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
