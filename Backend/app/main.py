
import time
from uuid import uuid4
from fastapi import FastAPI, Request
from app.api import router as api_router
from app.metrics import router as metrics_router
from app.logging_cfg import log_json

app = FastAPI(title="PayNow + Agent Assist (Backend)", version="0.4.0")

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or f"req_{uuid4().hex[:8]}"
    request.state.request_id = request_id
    t0 = time.time()
    try:
        response = await call_next(request)
        return response
    finally:
        latency = round((time.time() - t0) * 1000.0, 2)
        log_json(event="http_request",
                 requestId=request_id,
                 method=request.method,
                 path=str(request.url.path),
                 status=getattr(response, "status_code", 0),
                 latency_ms=latency)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
app.include_router(metrics_router)
