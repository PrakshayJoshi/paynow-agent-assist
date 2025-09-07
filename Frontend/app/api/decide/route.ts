
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const base = process.env.BACKEND_BASE || process.env.NEXT_PUBLIC_BACKEND_BASE || "http://localhost:8000";
  const apiKey = process.env.API_KEY; // optional

  const r = await fetch(`${base}/payments/decide`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: JSON.stringify(body),
  });

  const text = await r.text();
  return new NextResponse(text, {
    status: r.status,
    headers: { "Content-Type": r.headers.get("Content-Type") || "application/json" },
  });
}
