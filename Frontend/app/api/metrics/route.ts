export const dynamic = "force-dynamic";
import { NextRequest, NextResponse } from "next/server";

export async function GET(_: NextRequest) {
  const base = process.env.BACKEND_BASE || process.env.NEXT_PUBLIC_BACKEND_BASE || "http://localhost:8000";
  const r = await fetch(`${base}/metrics`, { cache: "no-store" });
  const text = await r.text();
  return new NextResponse(text, {
    status: r.status,
    headers: {
      "Content-Type": r.headers.get("Content-Type") || "application/json",
      "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
    },
  });
}
