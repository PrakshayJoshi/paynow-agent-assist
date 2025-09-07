
import time
from fastapi import HTTPException, status

RATE = 5.0  # tokens per second
BURST = 5.0

_buckets: dict[str, tuple[float, float]] = {}  # customerId -> (tokens, last_ts)

def check_rate_limit(customer_id: str):
    now = time.time()
    tokens, last_ts = _buckets.get(customer_id, (BURST, now))
    # refill
    elapsed = max(0.0, now - last_ts)
    tokens = min(BURST, tokens + elapsed * RATE)
    if tokens < 1.0:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    tokens -= 1.0
    _buckets[customer_id] = (tokens, now)
