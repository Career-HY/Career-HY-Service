from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from config.config import settings
from api.routers import user, profile, course, chatroom, chat
from db.session import get_db
from util.logging import setup_logging

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 로깅 시스템 초기화
setup_logging()

app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,
    same_site='none',
    https_only=True
)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(course.router)
app.include_router(chatroom.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi Backend!! 6/8 09:20 test"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"status": "ok"}
