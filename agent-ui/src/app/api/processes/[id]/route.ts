import { NextRequest, NextResponse } from "next/server";

const AGENTOS_URL =
  process.env.NEXT_PUBLIC_AGENTOS_URL || "http://localhost:7777";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const url = `${AGENTOS_URL}/api/processes/${id}`;

  try {
    const res = await fetch(url, { cache: "no-store" });
    if (res.status === 404) {
      return NextResponse.json(
        { error: "Processo não encontrado" },
        { status: 404 }
      );
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Falha ao conectar ao AgentOS" },
      { status: 503 }
    );
  }
}
