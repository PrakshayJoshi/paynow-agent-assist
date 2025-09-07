
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.models import PaymentRequest, DecisionResponse
from app.agent import Agent
from app.rules import decide
from app.security import verify_api_key
from app.ratelimit import check_rate_limit
from app.metrics import record_request
from app.logging_cfg import log_json, mask_customer
from app.storage import (
    SessionLocal, init_db, Idempotency, Case, get_or_create_balance, request_hash, get_lock
)

router = APIRouter()
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
    request: Request,
    _=Depends(verify_api_key),
    db: Session = Depends(get_db)
) -> DecisionResponse:
    t0 = time.time()
    request_id = getattr(request.state, "request_id", f"req_{uuid4().hex[:8]}")

    # 1) Rate limit per customerId
    check_rate_limit(req.customerId)

    # 2) Idempotency lookup
    rhash = request_hash(req.customerId, req.amount, req.currency, req.payeeId)
    existing = db.query(Idempotency).filter_by(key=req.idempotencyKey, customer_id=req.customerId).one_or_none()
    if existing and existing.req_hash == rhash:
        resp = existing.response_json
        record_request(resp.get("decision","review"), (time.time()-t0)*1000.0)
        log_json(event="decision_cached",
                 requestId=request_id,
                 decision=resp.get("decision"),
                 reasons=resp.get("reasons"),
                 customerId=mask_customer(req.customerId))
        return resp

    # 3) Agent & rules
    agent = Agent()
    agent.plan()

    # read real balance first from DB and log via agent tool with retry wrapper
    bal_row = get_or_create_balance(db, req.customerId)
    balance = float(bal_row.balance)
    agent.get_balance(req.customerId, balance)

    # risk signals (with retry/fallback guardrails)
    risk = agent.get_risk_signals(req.customerId, req.payeeId)

    decision, reasons = decide(req.amount, balance, risk)

    # 4) Reserve on allow (per-customer lock)
    if decision == "allow":
        lock = get_lock(req.customerId)
        with lock:
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
        db.rollback()

    # 6) Logs + Metrics
    log_json(event="decision",
             requestId=request_id,
             decision=decision,
             reasons=reasons,
             customerId=mask_customer(req.customerId))
    log_json(event="payment.decided",
             requestId=request_id,
             decision=decision,
             reasons=reasons,
             customerId=mask_customer(req.customerId))
    record_request(decision, (time.time()-t0)*1000.0)
    return response
