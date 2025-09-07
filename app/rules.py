
# Phase 2: deterministic rules returning (decision, reasons)
# def decide(amount, balance, risk): ...



from typing import Dict, List, Tuple

DAILY_THRESHOLD = 1000.0

def decide(amount: float, balance: float, risk: Dict) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    # Block if insufficient funds
    if amount > balance:
        return "block", ["insufficient_funds"]
    # Review if above threshold
    if amount > DAILY_THRESHOLD:
        reasons.append("amount_above_daily_threshold")
    # Review if risky
    if risk.get("recent_disputes", 0) >= 2 or bool(risk.get("device_change")):
        reasons.append("recent_disputes" if risk.get("recent_disputes", 0) >= 2 else "risk_signals")
    if reasons:
        return "review", reasons
    return "allow", []
