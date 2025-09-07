
# PayNow + Agent Assist — Full Submission

This repository contains both **Backend (FastAPI)** and **Frontend (Next.js + TS + Tailwind)** implementing the take‑home assignment.

## Quick start

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_KEY=local-dev-key
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

## Architecture (ASCII)
```
[Frontend (Next.js)]
  page.tsx (form, cURL, agent trace, latency)
  /api/decide     -> proxies to Backend POST /payments/decide
  /api/metrics    -> proxies to Backend GET /metrics

[Backend (FastAPI)]
  /payments/decide -> security (X-API-Key), rate limit (token bucket 5 rps / customer), idempotency (SQLite)
                    -> agent.plan -> tools: getBalance (logs actual DB balance), getRiskSignals
                       (tools wrapped with retry guardrails: max 2 retries + fallback)
                    -> rules (allow/review/block) + reasons
                    -> on allow: reserve funds (mutex + SQLite); on review/block: createCase
                    -> persist idempotent response and return {decision, reasons, agentTrace, requestId}
  /metrics         -> total requests, decision counts, rough p95
  Logs             -> JSON, requestId correlation, PII redaction of customerId
```
