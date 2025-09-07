
from fastapi import APIRouter
from typing import Dict

router = APIRouter()

_counters: Dict[str, int] = {
    "total_requests": 0,
    "decision_allow": 0,
    "decision_review": 0,
    "decision_block": 0,
}
_latencies: list[float] = []  # milliseconds, keep last 200

def record_request(decision: str, latency_ms: float):
    _counters["total_requests"] += 1
    if decision in ("allow","review","block"):
        _counters[f"decision_{decision}"] += 1
    _latencies.append(latency_ms)
    if len(_latencies) > 200:
        del _latencies[0]

def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    idx = int(0.95 * (len(arr)-1))
    return round(arr[idx], 2)

@router.get("/metrics")
def metrics():
    return {
        **_counters,
        "p95_latency_ms": p95(_latencies),
        "sample_size": len(_latencies),
    }
