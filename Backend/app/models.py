
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal

class PaymentRequest(BaseModel):
    customerId: str
    amount: float = Field(..., gt=0, description="Payment amount must be > 0")
    currency: str
    payeeId: str
    idempotencyKey: str

    @field_validator('customerId', 'payeeId', 'idempotencyKey')
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must be non-empty")
        return v.strip()

    @field_validator('currency')
    @classmethod
    def _currency_code(cls, v: str) -> str:
        import re
        if v is None:
            raise ValueError("currency is required")
        v = v.strip().upper()
        if not re.fullmatch(r'[A-Z]{3}', v):
            raise ValueError("currency must be 3 uppercase letters (e.g., USD, INR)")
        return v

class AgentStep(BaseModel):
    step: str
    detail: str

Decision = Literal['allow', 'review', 'block']

class DecisionResponse(BaseModel):
    decision: Decision
    reasons: List[str]
    agentTrace: List[AgentStep]
    requestId: str
