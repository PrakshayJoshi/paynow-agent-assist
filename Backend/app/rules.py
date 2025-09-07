
from typing import Dict, List, Tuple

DAILY_THRESHOLD = 1000.0

def decide(amount: float, balance: float, risk: Dict) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    if amount > balance:
        return "block", ["insufficient_funds"]
    if amount > DAILY_THRESHOLD:
        reasons.append("amount_above_daily_threshold")
    if risk.get("recent_disputes", 0) >= 2 or bool(risk.get("device_change")):
        if risk.get("recent_disputes", 0) >= 2:
            reasons.append("recent_disputes")
        else:
            reasons.append("risk_signals")
    if reasons:
        return "review", reasons
    return "allow", []
