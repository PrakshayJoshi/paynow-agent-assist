
# Frontend — Next.js + Tailwind (PayNow + Agent Assist)

## Run
```bash
npm install
npm run dev
# open http://localhost:3000
```

If backend URL differs, set:
```bash
echo 'NEXT_PUBLIC_BACKEND_BASE=http://localhost:8000' > .env.local
```

If backend requires API key, add server env so proxy sends header:
```bash
echo 'BACKEND_BASE=http://localhost:8000' >> .env.local
echo 'API_KEY=local-dev-key' >> .env.local
```

### Satisfies the FE items
- React/Next.js + TS + Tailwind
- Payment form → calls backend → renders decision, reasons, Agent Trace, requestId
- Observability: shows last-request latency; console timing friendly
- Security boundary: secrets only on server; basic error handling + 1 retry
- Accessible: labeled inputs, keyboard-friendly
