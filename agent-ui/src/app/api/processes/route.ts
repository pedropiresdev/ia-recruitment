import { NextRequest, NextResponse } from "next/server";

const AGENTOS_URL =
  process.env.NEXT_PUBLIC_AGENTOS_URL || "http://localhost:7777";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const params = searchParams.toString();
  const url = `${AGENTOS_URL}/api/processes${params ? `?${params}` : ""}`;

  try {
    const res = await fetch(url, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Falha ao conectar ao AgentOS" },
      { status: 503 }
    );
  }
}
