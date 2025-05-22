from sqlalchemy.orm import Session
from app.db import models
from app.schemas.user import UserCreate

def create_user(db: Session, user_in: UserCreate):
    db_user = models.User(**user_in.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
