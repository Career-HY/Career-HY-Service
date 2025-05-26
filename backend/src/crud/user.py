from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db import models
from schemas.user import UserCreate, UserLogin
from crud.profile import create_empty_profile
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(models.Member).filter(models.Member.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Member).filter(models.Member.id == user_id).first()

def create_user(db: Session, user_in: UserCreate):
    # 1) 중복 검사
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")
    
    # 2) UUID 생성 및 User 객체 생성
    user_id = str(uuid.uuid4())
    db_user = models.Member(id=user_id, **user_in.dict())
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
    
    # 5) 빈 프로필 자동 생성
    try:
        create_empty_profile(db, db_user.id)
    except Exception as e:
        # 프로필 생성 실패 시 사용자도 롤백
        db.delete(db_user)
        db.commit()
        raise HTTPException(status_code=500, detail="프로필 생성 중 오류가 발생했습니다")
    
    return db_user

def authenticate_user(db: Session, creds: UserLogin):
    user = get_user_by_email(db, creds.email)
    if not user or user.pwd != creds.pwd:
        return None
    return user