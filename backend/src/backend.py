from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from config.config import settings
from api.routers import user, profile, course, chatroom
from db.session import get_db
from util.logging import setup_logging

# 로깅 시스템 초기화
setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(course.router)
app.include_router(chatroom.router)

@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi Backend!! 5/31 20:50 test"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"status": "ok"}
