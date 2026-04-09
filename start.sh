#!/usr/bin/env bash
# Sobe todos os servidores MCP e depois o AgentOS na ordem correta.
# Uso: ./start.sh
# Para encerrar: Ctrl+C (mata todos os processos filhos)

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

cleanup() {
    echo ""
    echo "Encerrando servidores..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    exit 0
}
trap cleanup INT TERM

cd "$ROOT"

echo "Iniciando servidores MCP..."

uv run fastmcp run tools/job_opening_server.py:mcp \
    --transport streamable-http --port 8001 &
PIDS+=($!)

uv run fastmcp run tools/process_management_server.py:mcp \
    --transport streamable-http --port 8002 &
PIDS+=($!)

uv run fastmcp run tools/candidate_screening_server.py:mcp \
    --transport streamable-http --port 8003 &
PIDS+=($!)

uv run fastmcp run tools/interview_scheduling_server.py:mcp \
    --transport streamable-http --port 8004 &
PIDS+=($!)

uv run fastmcp run tools/recruitment_orchestrator_server.py:mcp \
    --transport streamable-http --port 8000 &
PIDS+=($!)

echo "Aguardando servidores MCP ficarem prontos..."
sleep 4

echo "Iniciando AgentOS..."
uv run python agentos.py &
PIDS+=($!)

echo ""
echo "Todos os serviços estão no ar:"
echo "  AgentOS          → http://localhost:7777"
echo "  orchestrator     → http://localhost:8000/mcp  ← endpoint para a LiGiaPro"
echo "  job-opening      → http://localhost:8001/mcp"
echo "  process-mgmt     → http://localhost:8002/mcp"
echo "  candidate        → http://localhost:8003/mcp"
echo "  scheduling       → http://localhost:8004/mcp"
echo ""
echo "Pressione Ctrl+C para encerrar tudo."

wait
