
# Backend — FastAPI (PayNow + Agent Assist)

Run locally (3 commands):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_KEY=local-dev-key && uvicorn app.main:app --reload
```
Health: http://localhost:8000/healthz

## POST /payments/decide
Sample cURL:
```bash
curl -X POST http://localhost:8000/payments/decide   -H "Content-Type: application/json"   -H "X-API-Key: $API_KEY"   -d '{"customerId":"c_123","amount":125.5,"currency":"USD","payeeId":"p_789","idempotencyKey":"uuid-1"}'
```

## Architecture (ASCII)
```
Client → POST /payments/decide
       → Auth (X-API-Key) + RateLimit (token bucket 5 rps per customer)
       → Idempotency lookup (SQLite)
       → Agent.plan + tools (getBalance, getRiskSignals) with retry/guardrails (max 2, fallback)
       → Rules → decision (allow/review/block)
       → On allow: reserve funds (mutex + SQLite)
         On review/block: createCase (SQLite)
       → Persist idempotent response
       → Return {decision, reasons, agentTrace, requestId}

Observability:
  - Logs: JSON with requestId, path, status, latency
  - /metrics: total requests, decision counts, p95 (rough)
```

## What we optimized
- Latency: small in-process metrics; minimal I/O; deterministic tools.
- Simplicity: FastAPI + SQLite; in-memory token bucket; small orchestrator.
- Security: API key; input validation; PII redaction in logs.

## Trade-offs
- In-memory RL vs Redis; SQLite vs Postgres; Python mutex vs DB row locks.

## Tests
```bash
PYTHONPATH=. pytest -q
```
- idempotency, rate limit, and a decision path.

## Simple evals
```bash
export API_KEY=local-dev-key
python scripts/run_eval.py eval_cases.json --base http://localhost:8000 --api-key $API_KEY
```
