
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"Content-Type": "application/json", "X-API-Key": "local-dev-key"}

def test_rate_limit_5_per_second():
    base = {
        "customerId":"RL_TEST",
        "amount": 10.0,
        "currency":"USD",
        "payeeId":"safe_vendor"
    }
    codes = []
    for i in range(6):
        payload = dict(base, idempotencyKey=f"rk{i}")
        r = client.post("/payments/decide", json=payload, headers=headers)
        codes.append(r.status_code)
    assert 429 in codes
