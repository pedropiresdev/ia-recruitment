"""
Verifica que cada servidor MCP responde corretamente ao protocolo MCP:
  - initialize   (handshake obrigatório)
  - tools/list   (descoberta de ferramentas)
  - tools/call   (execução de ferramenta)

Execute com os servidores rodando:
  uv run pytest -m integration tests/test_mcp_protocol.py -v
"""

import json
import os

import httpx
import pytest

pytestmark = pytest.mark.integration

# URLs dos servidores.
# - Local (padrão): cada servidor na sua porta (8001-8004).
# - Via gateway (staging/produção): defina MCP_BASE_URL (ex.: http://localhost)
#   e as rotas do Caddy (/mcp/<servidor>) são usadas.
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "").rstrip("/")

if MCP_BASE_URL:
    SERVERS = {
        "job-opening": f"{MCP_BASE_URL}/mcp/job-opening",
        "process-management": f"{MCP_BASE_URL}/mcp/process-management",
        "candidate-screening": f"{MCP_BASE_URL}/mcp/candidate-screening",
        "scheduling": f"{MCP_BASE_URL}/mcp/scheduling",
    }
else:
    SERVERS = {
        "job-opening": "http://localhost:8001/mcp",
        "process-management": "http://localhost:8002/mcp",
        "candidate-screening": "http://localhost:8003/mcp",
        "scheduling": "http://localhost:8004/mcp",
    }

# Ferramentas mínimas esperadas por servidor
EXPECTED_TOOLS = {
    "job-opening": {
        "create_job_opening",
        "collect_opening_details",
        "generate_job_description",
    },
    "process-management": {
        "list_processes",
        "get_sla_status",
        "get_process_detail",
        "suspend_process",
    },
    "candidate-screening": {
        "screen_candidate",
        "move_candidate_stage",
        "get_candidate_profile",
    },
    "scheduling": {"schedule_interview", "get_available_slots", "cancel_interview"},
}

# Chamadas mínimas para validar tools/call (inputs que não precisam de DB)
SMOKE_CALLS = {
    "process-management": {
        "name": "list_processes",
        "arguments": {"input": {}},
    },
    "scheduling": {
        "name": "get_scheduling_options",
        "arguments": {},
    },
}


# ─── helpers ──────────────────────────────────────────────────────────────────


class MCPClient:
    """Cliente mínimo do MCP streamable-http que mantém o mcp-session-id."""

    def __init__(self, url: str):
        self.url = url
        self.session_id: str | None = None
        self._next_id = 1

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers

    def post(self, method: str, params: dict, notification: bool = False) -> dict:
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            payload["id"] = self._next_id
            self._next_id += 1

        resp = httpx.post(self.url, json=payload, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        self.session_id = resp.headers.get("mcp-session-id", self.session_id)

        if notification:
            return {}

        # streamable-http pode responder como SSE; extrai o primeiro evento JSON
        if "text/event-stream" in resp.headers.get("content-type", ""):
            for line in resp.text.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
            pytest.fail(f"SSE response sem dados: {resp.text[:300]}")

        return resp.json()


def _initialize(url: str) -> tuple[MCPClient, dict]:
    client = MCPClient(url)
    body = client.post(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "0.1"},
        },
    )
    client.post("notifications/initialized", {}, notification=True)
    return client, body


def _tools_list(client: MCPClient) -> list[dict]:
    body = client.post("tools/list", {})
    assert "result" in body, f"tools/list sem 'result': {body}"
    return body["result"].get("tools", [])


def _tools_call(client: MCPClient, tool_name: str, arguments: dict) -> dict:
    body = client.post("tools/call", {"name": tool_name, "arguments": arguments})
    assert "result" in body, f"tools/call sem 'result': {body}"
    return body["result"]


# ─── testes ───────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("server_name,url", SERVERS.items())
def test_initialize(server_name: str, url: str):
    """Handshake MCP deve retornar serverInfo e protocolVersion."""
    _, body = _initialize(url)
    assert "result" in body, f"[{server_name}] initialize sem 'result': {body}"
    result = body["result"]
    assert "serverInfo" in result, f"[{server_name}] serverInfo ausente"
    assert "protocolVersion" in result, f"[{server_name}] protocolVersion ausente"


@pytest.mark.parametrize("server_name,url", SERVERS.items())
def test_tools_list(server_name: str, url: str):
    """tools/list deve expor pelo menos as ferramentas mínimas esperadas."""
    client, _ = _initialize(url)
    tools = _tools_list(client)

    assert len(tools) > 0, f"[{server_name}] tools/list retornou lista vazia"

    exposed = {t["name"] for t in tools}
    expected = EXPECTED_TOOLS[server_name]
    missing = expected - exposed
    assert not missing, (
        f"[{server_name}] ferramentas ausentes em tools/list: {missing}\n"
        f"Expostas: {exposed}"
    )


@pytest.mark.parametrize("server_name,url", SERVERS.items())
def test_tools_list_schema_contract(server_name: str, url: str):
    """Cada ferramenta deve ter name, description e inputSchema com type=object."""
    client, _ = _initialize(url)
    tools = _tools_list(client)

    for tool in tools:
        name = tool.get("name", "<sem nome>")
        assert "name" in tool, f"[{server_name}:{name}] campo 'name' ausente"
        assert "description" in tool, (
            f"[{server_name}:{name}] campo 'description' ausente"
        )
        assert "inputSchema" in tool, (
            f"[{server_name}:{name}] campo 'inputSchema' ausente"
        )

        schema = tool["inputSchema"]
        assert schema.get("type") == "object", (
            f"[{server_name}:{name}] inputSchema.type deve ser 'object', "
            f"recebido: {schema.get('type')}"
        )


@pytest.mark.parametrize("server_name,call", SMOKE_CALLS.items())
def test_tools_call_smoke(server_name: str, call: dict):
    """tools/call deve executar sem erro para inputs mínimos (sem DB)."""
    url = SERVERS[server_name]
    client, _ = _initialize(url)

    result = _tools_call(client, call["name"], call["arguments"])
    assert result is not None, f"[{server_name}] tools/call retornou None"
    # Não valida conteúdo — apenas que o servidor respondeu sem jsonrpc error
