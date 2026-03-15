import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXUS_API_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  const url = new URL(req.url);
  const path = url.searchParams.get("path");

  if (!path) {
    return NextResponse.json({ error: "Missing path parameter" }, { status: 400 });
  }

  const body = await req.json();

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const path = url.searchParams.get("path");

  if (!path) {
    return NextResponse.json({ error: "Missing path parameter" }, { status: 400 });
  }

  const res = await fetch(`${API_BASE}${path}`);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
