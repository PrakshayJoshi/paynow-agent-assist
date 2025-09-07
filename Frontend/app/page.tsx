
"use client";
import React, { useEffect, useMemo, useState } from "react";

type AgentStep = { step: string; detail: string };
type DecisionResp = {
  decision: "allow" | "review" | "block";
  reasons: string[];
  agentTrace: AgentStep[];
  requestId: string;
};

const cls = (...xs: (string | false | undefined)[]) => xs.filter(Boolean).join(" ");
const uuid = () =>
  (typeof crypto !== "undefined" && (crypto as any).randomUUID
    ? (crypto as any).randomUUID()
    : Math.random().toString(16).slice(2) + Date.now().toString(16));

export default function Page() {
  const [customerId, setCustomerId] = useState("c_123");
  const [amount, setAmount] = useState(125.5);
  const [currency, setCurrency] = useState("USD");
  const [payeeId, setPayeeId] = useState("p_789");
  const [idem, setIdem] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resp, setResp] = useState<DecisionResp | null>(null);
  const [metrics, setMetrics] = useState<any | null>(null);
  const [lastLatency, setLastLatency] = useState<number | null>(null);

  useEffect(() => { setIdem(uuid()); }, []);

  const backendBase = process.env.NEXT_PUBLIC_BACKEND_BASE || "http://localhost:8000";

  const curl = useMemo(() => {
    const payload = JSON.stringify({ customerId, amount, currency, payeeId, idempotencyKey: idem || "<idempotencyKey>" });
    return `curl -X POST ${backendBase}/payments/decide \\n  -H \"Content-Type: application/json\" \\\n  -d '${payload}'`;
  }, [backendBase, customerId, amount, currency, payeeId, idem]);

  const submit = async () => {
    setLoading(true); setError(null);
    const payload = { customerId, amount, currency, payeeId, idempotencyKey: idem || uuid() };
    const t0 = performance.now();
    try {
      let r: Response | null = null;
      try {
        r = await fetch("/api/decide", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      } catch (e) {
        await new Promise(res => setTimeout(res, 150));
        r = await fetch("/api/decide", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      }
      if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
      const j: DecisionResp = await r.json();
      setResp(j);
      setIdem(uuid());
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLastLatency(Math.round(performance.now() - t0));
      setLoading(false);
    }
  };

  const refreshMetrics = async () => {
    setError(null);
    try {
      const r = await fetch(`/api/metrics?ts=${Date.now()}`, { cache: "no-store" });
      if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
      setMetrics(await r.json());
    } catch (e: any) {
      setError(e.message || String(e));
    }
  };

  const decisionColor =
    resp?.decision === "allow"
      ? "text-emerald-700"
      : resp?.decision === "review"
      ? "text-amber-700"
      : "text-rose-700";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-6xl p-6 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">PayNow + Agent Assist</h1>
          <a className="text-sm underline opacity-70 hover:opacity-100" href="#" onClick={(e) => { e.preventDefault(); navigator.clipboard.writeText(curl); }}>
            Copy backend cURL
          </a>
        </header>

        <section className="grid md:grid-cols-3 gap-4">
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <h2 className="font-semibold mb-3">Backend</h2>
            <div className="text-sm text-slate-600">
              Using proxy to <code>/api/decide</code> and <code>/api/metrics</code>.<br/>
              Backend base: <code>{backendBase}</code>
            </div>
            <button onClick={refreshMetrics} className="mt-4 inline-flex items-center rounded-xl border bg-slate-900 text-white px-3 py-2 text-sm hover:opacity-90">
              Refresh Metrics
            </button>
            {metrics && (
              <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                <Metric label="Total" value={metrics.total_requests} />
                <Metric label="p95 (ms)" value={metrics.p95_latency_ms} />
                <Metric label="Allow" value={metrics.decision_allow} />
                <Metric label="Review" value={metrics.decision_review} />
                <Metric label="Block" value={metrics.decision_block} />
              </div>
            )}
          </div>

          <div className="rounded-2xl border bg-white p-4 shadow-sm md:col-span-2">
            <h2 className="font-semibold mb-3">Create Payment</h2>
            <div className="grid md:grid-cols-2 gap-3">
              <Field label="Customer ID"><input id="customerId" value={customerId} onChange={e=>setCustomerId(e.target.value)} className="w-full rounded-xl border px-3 py-2" /></Field>
              <Field label="Payee ID"><input id="payeeId" value={payeeId} onChange={e=>setPayeeId(e.target.value)} className="w-full rounded-xl border px-3 py-2" /></Field>
              <Field label="Amount"><input id="amount" type="number" step="0.01" value={amount} onChange={e=>setAmount(Number(e.target.value))} className="w-full rounded-xl border px-3 py-2" /></Field>
              <Field label="Currency"><input id="currency" value={currency} onChange={e=>setCurrency(e.target.value.toUpperCase())} className="w-full rounded-xl border px-3 py-2" /></Field>
              <Field label="Idempotency Key">
                <div className="flex gap-2">
                  <input id="idempotencyKey" value={idem} onChange={e=>setIdem(e.target.value)} className="w-full rounded-xl border px-3 py-2" />
                  <button onClick={()=>setIdem(uuid())} className="rounded-xl border px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200">New</button>
                </div>
              </Field>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              <ScenarioButton label="Review (disputes)" onClick={()=>{setCustomerId("c_123"); setPayeeId("p_789"); setAmount(125.5); setCurrency("USD"); setIdem(uuid());}} />
              <ScenarioButton label="Allow (safe vendor)" onClick={()=>{setCustomerId("user_allow_"+Math.random().toString(16).slice(2)); setPayeeId("safe_vendor"); setAmount(200); setCurrency("USD"); setIdem(uuid());}} />
              <ScenarioButton label="Block (insufficient)" onClick={()=>{setCustomerId("c_small"); setPayeeId("safe_vendor"); setAmount(400); setCurrency("USD"); setIdem(uuid());}} />
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button disabled={loading} onClick={submit} className={cls("inline-flex items-center rounded-xl border px-4 py-2", loading ? "bg-slate-300 text-slate-600" : "bg-slate-900 text-white hover:opacity-90")}>
                {loading ? "Submitting…" : "Submit payment"}
              </button>
              {lastLatency !== null && <span className="text-xs text-slate-500">Last request latency: <b>{lastLatency} ms</b></span>}
            </div>

            {error && <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-rose-700 text-sm">{String(error)}</div>}
          </div>
        </section>

        {resp && (
          <section className="rounded-2xl border bg-white p-4 shadow-sm">
            <div className="mt-2 inline-flex items-center gap-2 rounded-xl border px-3 py-1 text-sm">
              <span className={cls("font-semibold uppercase tracking-wide", decisionColor)}>{resp.decision}</span>
              {resp.reasons.length > 0 && <span className="text-slate-400">•</span>}
              {resp.reasons.map((r, i) => <span key={i} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs border">{r}</span>)}
              <span className="text-slate-400">•</span>
              <span className="text-xs text-slate-600">req: {resp.requestId}</span>
            </div>
            <div className="mt-3">
              <ol className="relative border-s border-slate-200 ml-3">
                {resp.agentTrace.map((s, i) => (
                  <li key={i} className="ms-4 py-2">
                    <div className="absolute -start-1.5 mt-2 h-3 w-3 rounded-full bg-slate-300 border"></div>
                    <div className="font-mono text-xs text-slate-500">{s.step}</div>
                    <div className="text-sm">{s.detail}</div>
                  </li>
                ))}
              </ol>
            </div>
          </section>
        )}

        <section className="rounded-2xl border bg-white p-4 shadow-sm">
          <h3 className="font-semibold mb-2">Sample Backend cURL</h3>
          <pre className="rounded-xl bg-slate-950 text-slate-50 p-3 text-xs overflow-x-auto">
            <code suppressHydrationWarning>{curl}</code>
          </pre>
        </section>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <div className="text-sm mb-1 text-slate-700">{label}</div>
      {children}
    </label>
  );
}

function Metric({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-xl border bg-slate-50 p-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="text-sm font-semibold">{String(value)}</div>
    </div>
  );
}

function ScenarioButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className="rounded-xl border px-3 py-1 text-xs bg-slate-100 hover:bg-slate-200">{label}</button>
  );
}
