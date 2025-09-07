
from fastapi import FastAPI

app = FastAPI(title="PayNow + Agent Assist (Backend)", version="0.1.0")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
