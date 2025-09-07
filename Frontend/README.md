
    # PayNow + Agent Assist — Frontend (Next.js + Tailwind, TypeScript)

    Minimal UI to send a payment to the backend and display **decision | reasons | agentTrace | requestId**.

- Form for amount/payee/idempotency
- Proxy server routes: `/api/decide` and `/api/metrics`
- Timeline for **agentTrace**; colored decision badge; metrics peek

## Run
```bash
npm install
npm run dev
# open http://localhost:3000
```

Set backend base if not default:
```bash
echo 'NEXT_PUBLIC_BACKEND_BASE=http://localhost:8000' > .env.local
```
Add API key only if your backend requires it:
```bash
echo 'BACKEND_BASE=http://localhost:8000' >> .env.local
echo 'API_KEY=local-dev-key' >> .env.local
```

## Satisfies the brief
- FE: **React/Next.js + TS + Tailwind**
- Core flow: user enters payment → returns **decision | reasons | agentTrace | requestId**
- Agent trace surfaced clearly (timeline)
- Defense-in-depth: secrets (if any) stay server-side; no PII logging
- README + simple route (index `/`)
