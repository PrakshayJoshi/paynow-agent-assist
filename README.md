
# PayNow + Agent Assist (Backend) — FastAPI

A tiny, **production-minded** slice of a banking flow. A customer initiates a payment and an **agentic orchestrator** performs checks and returns a decision: **allow | review | block**, with **reasons** and an **agent trace** showing what was checked and why.

---

## Run locally (3 commands)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_KEY=local-dev-key && uvicorn app.main:app --reload
```

Health check: http://localhost:8000/healthz

---

## API

### POST `/payments/decide`
**Request**
```json
{
  "customerId": "c_123",
  "amount": 125.50,
  "currency": "USD",
  "payeeId": "p_789",
  "idempotencyKey": "uuid-1"
}
```

**Response (example)**
```json
{
  "decision": "review",
  "reasons": ["recent_disputes"],
  "agentTrace": [
    {"step":"plan","detail":"Check balance, risk, and limits"},
    {"step":"tool:getBalance","detail":"balance=300.00"},
    {"step":"tool:getRiskSignals","detail":"recent_disputes=2, device_change=true"},
    {"step":"tool:recommend","detail":"route to manual review"}
  ],
  "requestId": "req_abc12345"
}
```

**Sample cURL**
```bash
curl -X POST http://localhost:8000/payments/decide   -H "Content-Type: application/json"   -H "X-API-Key: $API_KEY"   -d '{"customerId":"c_123","amount":125.5,"currency":"USD","payeeId":"p_789","idempotencyKey":"uuid-1"}'
```

---

## Architecture (ASCII)

```
Client → POST /payments/decide
       → Auth (X-API-Key) + RateLimit (per customerId; token bucket 5 rps)
       → Idempotency lookup (SQLite)
       → Agent.plan → Agent.tools (getBalance, getRiskSignals)
       → Rules → decision (allow/review/block)
       → On allow: reserve funds (per-customer in-memory lock; update SQLite)
         On review/block: createCase (SQLite)
       → Persist idempotent response → Return {decision, reasons, agentTrace, requestId}

Observability:
  - Logs: JSON lines with requestId, path, status, latency_ms
  - /metrics: total_requests, decision counts, p95_latency_ms (rough)
```

---

## What I optimized
- **Latency:** pre-validation; small in-process metrics; minimal I/O; deterministic tools.
- **Simplicity:** FastAPI + SQLite; in-memory token bucket; small orchestrator (no heavy AI libs).
- **Security:** API key on all calls; input validation; PII redaction in logs (mask customerId).

## Trade-offs
- **In-memory rate limiter** vs Redis: simplicity now, not distributed (OK for local take-home).
- **SQLite** vs Postgres: zero-setup and fine for a demo; less realistic for concurrent writes.
- **Per-customer lock** vs DB row-locking: SQLite lacks `FOR UPDATE`, so a Python mutex is used.

---

## Agentic orchestrator
- Plan → Tool calls → Recommendation note in `agentTrace`
- Tools: `getBalance`, `getRiskSignals` (stubs; deterministic)
- Guardrails: simple implementation with deterministic outputs; easy to add max-retry wrappers
- No external LLMs—**deterministic stubs** to keep the demo repeatable

---

## Observability
- **Logs:** JSON lines with `event`, `requestId`, `method`, `path`, `status`, `latency_ms`. Also decision logs with masked PII.
- **Metrics:** `GET /metrics` returns counters and a rough `p95_latency_ms` over a small rolling window.

---

## Tests
Run:
```bash
PYTHONPATH=. pytest -q
```
Covers:
- **Idempotency:** same payload + key returns identical response.
- **Rate limit:** 6 rapid calls for the same customer → at least one 429.
- **Decision path:** allow once, then block due to insufficient funds.

---

## Nice-to-have: Event publish
A simple event line is logged to stdout (`event="payment.decided"`) after each decision.

---

## Simple evals
Use `eval_cases.json` to verify expected decisions:
```bash
python scripts/run_eval.py eval_cases.json --base http://localhost:8000 --api-key $API_KEY
```
Output:
```
✅ 5/5 correct
```

---

## Screenshots/GIF (suggested for submission)
- cURL call to `/payments/decide` (review + allow + block examples)
- `/metrics` output
- Terminal logs showing decision + requestId
- Passing tests (`pytest -q`)
- Architecture diagram (this ASCII block or a PNG)

---

## Folder layout
```
app/
  main.py         # FastAPI app, requestId middleware, mounts /metrics and API router
  api.py          # POST /payments/decide (security, RL, idempotency, reserve, metrics)
  models.py       # Pydantic models (PaymentRequest, DecisionResponse, AgentStep)
  agent.py        # Orchestrator (plan + tools) and trace
  rules.py        # Deterministic decision rules
  storage.py      # SQLite models: Idempotency, Balance, Case (+ simple per-customer lock)
  ratelimit.py    # In-memory token bucket (5 rps per customer)
  security.py     # X-API-Key validation
  metrics.py      # Counters and p95; GET /metrics
  logging_cfg.py  # JSON logging + PII masking

tests/
  test_idempotency.py
  test_rate_limit.py
  test_decision.py

scripts/
  run_eval.py

README.md
requirements.txt
```

---

## TODOs / Potential extensions
- Replace in-memory rate limiter with Redis for distributed scenarios
- Add integration tests and fault-injection around agent tools
- Add Dockerfile + GitHub Actions CI
- Expand risk signals (velocity checks, geo, device fingerprinting)
