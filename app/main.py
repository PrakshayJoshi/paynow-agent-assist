
from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="PayNow + Agent Assist (Backend)", version="0.2.0")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
