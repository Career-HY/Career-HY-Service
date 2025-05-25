from fastapi import FastAPI

app = FastAPI(title="Ingestion API")

@app.get("/")
def root():
    return {"message": "Welcome to Career-Hi Ingestion API!"}


