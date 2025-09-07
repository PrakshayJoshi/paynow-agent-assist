
# Placeholder for API routes (Phase 1 will add POST /payments/decide here)
# from fastapi import APIRouter
# router = APIRouter()
# ... define endpoints and include in main.py later



from fastapi import APIRouter
from uuid import uuid4

from app.models import PaymentRequest, DecisionResponse, AgentStep
from app.agent import Agent
from app.rules import decide

router = APIRouter()

@router.post("/payments/decide", response_model=DecisionResponse)
def payments_decide(req: PaymentRequest) -> DecisionResponse:
    # In Phase 3 we'll add API key, rate limit, idempotency, etc.
    request_id = f"req_{uuid4().hex[:8]}"
    agent = Agent()
    agent.plan()
    balance = agent.get_balance(req.customerId)
    risk = agent.get_risk_signals(req.customerId, req.payeeId)
    decision, reasons = decide(req.amount, balance, risk)
    # Add a human-ish note in trace (no LLM; just template)
    if decision == "review":
        agent.recommend_note("route to manual review")
    elif decision == "block":
        agent.recommend_note("block due to rule violation")
    else:
        agent.recommend_note("allow")

    return DecisionResponse(
        decision=decision,
        reasons=reasons,
        agentTrace=agent.trace,
        requestId=request_id
    )
