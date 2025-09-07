
# Phase 2: plain orchestrator 'Agent' with plan() + tool calls (getBalance, getRiskSignals, createCase)
# Include simple retries (max 2) and append steps to agentTrace
# class Agent: ...

from typing import Dict, Any, List
from app.models import AgentStep

class Agent:
    def __init__(self):
        self.trace: List[AgentStep] = []

    def plan(self) -> None:
        self.trace.append(AgentStep(step="plan", detail="Check balance, risk, and limits"))

    # In a later phase, this will query DB
    def get_balance(self, customer_id: str) -> float:
        balance = 300.00
        self.trace.append(AgentStep(step="tool:getBalance", detail=f"balance={balance:.2f}"))
        return balance

    # In a later phase, this will query a risk service
    def get_risk_signals(self, customer_id: str, payee_id: str) -> Dict[str, Any]:
        risk = {"recent_disputes": 2, "device_change": True}
        detail = f"recent_disputes={risk['recent_disputes']}, device_change={str(risk['device_change']).lower()}"
        self.trace.append(AgentStep(step="tool:getRiskSignals", detail=detail))
        return risk

    def recommend_note(self, note: str) -> None:
        self.trace.append(AgentStep(step="tool:recommend", detail=note))
