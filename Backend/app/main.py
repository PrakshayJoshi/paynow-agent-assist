
import time
from uuid import uuid4
from fastapi import FastAPI, Request
from app.api import router as api_router
from app.metrics import router as metrics_router
from app.logging_cfg import log_json

app = FastAPI(title="PayNow + Agent Assist (Backend)", version="1.0.0")

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or f"req_{uuid4().hex[:8]}"
    request.state.request_id = request_id
    t0 = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        latency = round((time.perf_counter() - t0) * 1000.0, 2)
        log_json(event="http_request_error",
                 requestId=request_id, method=request.method, path=str(request.url.path),
                 error=str(e), latency_ms=latency)
        raise
    finally:
        latency = round((time.perf_counter() - t0) * 1000.0, 2)
        status_code = getattr(response, "status_code", 500)
        log_json(event="http_request",
                 requestId=request_id, method=request.method, path=str(request.url.path),
                 status=status_code, latency_ms=latency)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
app.include_router(metrics_router)
