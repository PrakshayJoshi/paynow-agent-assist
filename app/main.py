
from fastapi import FastAPI
from app.api import router as api_router
from app.metrics import router as metrics_router

app = FastAPI(title="PayNow + Agent Assist (Backend)", version="0.3.0")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
app.include_router(metrics_router)
