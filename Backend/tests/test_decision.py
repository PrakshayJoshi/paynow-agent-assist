
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"Content-Type": "application/json", "X-API-Key": "local-dev-key"}

def test_decision_paths_allow_then_block_on_insufficient():
    p1 = {
        "customerId":"DECIDE_USER",
        "amount": 250.0,
        "currency":"USD",
        "payeeId":"safe_vendor",
        "idempotencyKey":"d1"
    }
    p2 = dict(p1, idempotencyKey="d2", amount=100.0)
    r1 = client.post("/payments/decide", json=p1, headers=headers)
    r2 = client.post("/payments/decide", json=p2, headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["decision"] == "allow"
    assert r2.json()["decision"] in ("block","review")
