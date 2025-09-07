
# PayNow + Agent Assist (Backend) — Phase 0

Minimal scaffold for the FastAPI backend.

## Run locally (3 commands)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Smoke test
```bash
pytest -q
```

## Health check
Open: http://localhost:8000/healthz → `{"status":"ok"}`

## Next phases
- Phase 1: Pydantic models + POST `/payments/decide`
- Phase 2: Agent (plan + tools) + rules
- Phase 3: Security, Idempotency, Rate limit, Concurrency, Metrics, Logging
- Phase 4: Tests & README polish
