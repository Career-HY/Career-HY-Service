from fastapi import FastAPI
from config.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# 라우터 등록

@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi Backend!"}
