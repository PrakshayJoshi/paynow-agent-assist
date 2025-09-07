
from __future__ import annotations
from typing import Dict, Any, List, Callable, TypeVar
import time
from app.models import AgentStep

T = TypeVar("T")

class Agent:
    def __init__(self):
        self.trace: List[AgentStep] = []

    def plan(self) -> None:
        self.trace.append(AgentStep(step="plan", detail="Check balance, risk, and limits"))

    # --- guardrails: simple retry wrapper with max 2 retries and fallback ---
    def _with_retry(self, name: str, fn: Callable[[], T], fallback: T, max_retries: int = 2) -> T:
        attempt = 0
        while True:
            try:
                return fn()
            except Exception as e:
                attempt += 1
                self.trace.append(AgentStep(step=f"tool:{name}:retry", detail=f"attempt={attempt}, error={type(e).__name__}"))
                if attempt > max_retries:
                    self.trace.append(AgentStep(step=f"tool:{name}:fallback", detail=f"using fallback"))
                    return fallback
                time.sleep(0.01 * attempt)

    def get_balance(self, customer_id: str, balance: float) -> float:
        def _do() -> float:
            return balance
        val = self._with_retry("getBalance", _do, balance)
        self.trace.append(AgentStep(step="tool:getBalance", detail=f"balance={val:.2f}"))
        return val

    def get_risk_signals(self, customer_id: str, payee_id: str) -> Dict[str, Any]:
        def _do() -> Dict[str, Any]:
            if str(payee_id).lower().startswith("safe"):
                return {"recent_disputes": 0, "device_change": False}
            return {"recent_disputes": 2, "device_change": True}
        risk = self._with_retry("getRiskSignals", _do, {"recent_disputes": 0, "device_change": False})
        detail = f"recent_disputes={risk['recent_disputes']}, device_change={str(risk['device_change']).lower()}"
        self.trace.append(AgentStep(step="tool:getRiskSignals", detail=detail))
        return risk

    def recommend_note(self, note: str) -> None:
        self.trace.append(AgentStep(step="tool:recommend", detail=note))
