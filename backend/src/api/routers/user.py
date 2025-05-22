from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.crud.user import create_user, get_user_by_name
from app.db.session import get_db

router = APIRouter()

@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_name(db, user_in.username):
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다")
    user = create_user(db, user_in)
    return user
