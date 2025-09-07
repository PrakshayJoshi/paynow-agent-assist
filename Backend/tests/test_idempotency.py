
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"Content-Type": "application/json", "X-API-Key": "local-dev-key"}

def test_idempotency_returns_same_response():
    payload = {
        "customerId":"IDEMP_USER",
        "amount": 50.0,
        "currency":"USD",
        "payeeId":"safe_vendor",
        "idempotencyKey":"IDEMP_KEY"
    }
    r1 = client.post("/payments/decide", json=payload, headers=headers)
    r2 = client.post("/payments/decide", json=payload, headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200
    j1, j2 = r1.json(), r2.json()
    assert j1 == j2  # identical (includes same requestId from cache)
