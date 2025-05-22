from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import models
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    # 1) 중복 검사
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")
    
    # 2) User 객체 생성
    db_user = models.User(**user_in.dict())
    db.add(db_user)

    try:
        # 3) 커밋 시도
        db.commit()
    except IntegrityError:
        # UNIQUE 제약을 다시 위반하면 롤백 후 예외 처리
        db.rollback()
        raise HTTPException(status_code=400, detail="데이터베이스 제약 조건 위반")

    # 4) 최신 상태로 동기화
    db.refresh(db_user)
    return db_user
