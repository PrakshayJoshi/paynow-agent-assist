
from __future__ import annotations
import json
import hashlib
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///./data.db", future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()

class Idempotency(Base):
    __tablename__ = "idempotency"
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    req_hash = Column(String, nullable=False)
    response_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("key", "customer_id", name="uq_key_customer"),)

class Balance(Base):
    __tablename__ = "balances"
    customer_id = Column(String, primary_key=True)
    balance = Column(Float, nullable=False, default=300.0)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, nullable=False)
    payee_id = Column(String, nullable=False)
    reasons = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def init_db():
    Base.metadata.create_all(engine)

def request_hash(customer_id: str, amount: float, currency: str, payee_id: str) -> str:
    payload = json.dumps(
        {"customerId": customer_id, "amount": amount, "currency": currency, "payeeId": payee_id},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def get_or_create_balance(session, customer_id: str) -> Balance:
    bal = session.get(Balance, customer_id)
    if not bal:
        bal = Balance(customer_id=customer_id, balance=300.0)
        session.add(bal)
        session.commit()
    return bal

# Simple per-customer in-memory concurrency locks
from threading import Lock
_locks: dict[str, Lock] = {}

def get_lock(customer_id: str) -> Lock:
    if customer_id not in _locks:
        _locks[customer_id] = Lock()
    return _locks[customer_id]
