from fastapi import FastAPI, Depends
from config.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi Backend!"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"status": "ok"}
