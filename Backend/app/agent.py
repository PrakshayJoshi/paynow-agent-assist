from app.models import AgentStep

class Agent:
    def __init__(self):
        self.trace: list[AgentStep] = []

    def plan(self) -> None:
        self.trace.append(AgentStep(step="plan", detail="Check balance, risk, and limits"))

    # accept the real balance and log it
    def get_balance(self, customer_id: str, balance: float) -> float:
        self.trace.append(AgentStep(step="tool:getBalance", detail=f"balance={balance:.2f}"))
        return balance

    def get_risk_signals(self, customer_id: str, payee_id: str) -> dict:
        if str(payee_id).lower().startswith("safe"):
            risk = {"recent_disputes": 0, "device_change": False}
        else:
            risk = {"recent_disputes": 2, "device_change": True}
        self.trace.append(AgentStep(step="tool:getRiskSignals",
                                    detail=f"recent_disputes={risk['recent_disputes']}, device_change={str(risk['device_change']).lower()}"))
        return risk

    def recommend_note(self, note: str) -> None:
        self.trace.append(AgentStep(step="tool:recommend", detail=note))
