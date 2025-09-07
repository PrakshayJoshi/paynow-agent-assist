
import json
import time
from uuid import uuid4
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import PaymentRequest, DecisionResponse
from app.agent import Agent
from app.rules import decide
from app.security import verify_api_key
from app.ratelimit import check_rate_limit
from app.metrics import record_request
from app.storage import (
    SessionLocal, init_db, Idempotency, Case, get_or_create_balance, request_hash, get_lock
)

router = APIRouter()

# Ensure DB tables exist at import time (simple for local dev)
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/payments/decide", response_model=DecisionResponse)
def payments_decide(
    req: PaymentRequest,
    _=Depends(verify_api_key),
    db: Session = Depends(get_db)
) -> DecisionResponse:
    t0 = time.time()
    request_id = f"req_{uuid4().hex[:8]}"

    # 1) Rate limit per customerId
    check_rate_limit(req.customerId)

    # 2) Idempotency lookup
    rhash = request_hash(req.customerId, req.amount, req.currency, req.payeeId)
    existing = db.query(Idempotency).filter_by(key=req.idempotencyKey, customer_id=req.customerId).one_or_none()
    if existing and existing.req_hash == rhash:
        resp = existing.response_json
        # record metrics and return cached
        record_request(resp.get("decision","review"), (time.time()-t0)*1000.0)
        return resp

    # 3) Agent & rules
    agent = Agent()
    agent.plan()
    balance_trace = agent.get_balance(req.customerId)  # trace only
    risk = agent.get_risk_signals(req.customerId, req.payeeId)
    # True balance from DB for reservation
    bal_row = get_or_create_balance(db, req.customerId)
    balance = float(bal_row.balance)
    decision, reasons = decide(req.amount, balance, risk)

    # 4) Reserve on allow (concurrency-safe with per-customer lock)
    if decision == "allow":
        lock = get_lock(req.customerId)
        with lock:
            # re-read
            bal_row = get_or_create_balance(db, req.customerId)
            if bal_row.balance < req.amount:
                decision = "block"
                reasons = ["insufficient_funds"]
            else:
                bal_row.balance = bal_row.balance - req.amount
                db.add(bal_row)
                db.commit()

        agent.recommend_note("allow")
    elif decision == "review":
        # create a case
        case = Case(customer_id=req.customerId, payee_id=req.payeeId, reasons=reasons)
        db.add(case)
        db.commit()
        agent.recommend_note("route to manual review")
    else:
        agent.recommend_note("block due to rule violation")

    response = {
        "decision": decision,
        "reasons": reasons,
        "agentTrace": [s.model_dump() for s in agent.trace],
        "requestId": request_id,
    }

    # 5) Persist idempotent response
    idem = Idempotency(key=req.idempotencyKey, customer_id=req.customerId, req_hash=rhash, response_json=response)
    try:
        db.add(idem)
        db.commit()
    except Exception:
        db.rollback()  # swallow unique conflicts as it's safe

    # 6) Metrics
    record_request(decision, (time.time()-t0)*1000.0)
    return response
