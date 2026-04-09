"""
Verifica que cada servidor MCP responde corretamente ao protocolo MCP:
  - initialize   (handshake obrigatório)
  - tools/list   (descoberta de ferramentas)
  - tools/call   (execução de ferramenta)

Execute com os servidores rodando:
  uv run pytest tests/test_mcp_protocol.py -v
"""

import pytest
import httpx

# URLs dos servidores — sobrescreva com variáveis de ambiente se necessário
SERVERS = {
    "job-opening":        "http://localhost:8001/mcp",
    "process-management": "http://localhost:8002/mcp",
    "candidate-screening":"http://localhost:8003/mcp",
    "scheduling":         "http://localhost:8004/mcp",
}

# Ferramentas mínimas esperadas por servidor
EXPECTED_TOOLS = {
    "job-opening":        {"create_job_opening", "collect_opening_details", "generate_job_description"},
    "process-management": {"list_processes", "get_sla_status", "get_process_detail", "suspend_process"},
    "candidate-screening":{"screen_candidate", "move_candidate_stage", "get_candidate_profile"},
    "scheduling":         {"schedule_interview", "get_available_slots", "cancel_interview"},
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

def _post(url: str, method: str, params: dict, req_id: int) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    resp = httpx.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()

    # streamable-http pode responder como SSE; extrai o primeiro evento JSON
    content_type = resp.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for line in resp.text.splitlines():
            if line.startswith("data:"):
                import json
                return json.loads(line[5:].strip())
        pytest.fail(f"SSE response sem dados: {resp.text[:300]}")

    return resp.json()


def _initialize(url: str) -> dict:
    return _post(
        url,
        method="initialize",
        params={
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "0.1"},
        },
        req_id=1,
    )


def _tools_list(url: str) -> list[dict]:
    body = _post(url, method="tools/list", params={}, req_id=2)
    assert "result" in body, f"tools/list sem 'result': {body}"
    return body["result"].get("tools", [])


def _tools_call(url: str, tool_name: str, arguments: dict) -> dict:
    body = _post(
        url,
        method="tools/call",
        params={"name": tool_name, "arguments": arguments},
        req_id=3,
    )
    assert "result" in body, f"tools/call sem 'result': {body}"
    return body["result"]


# ─── testes ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("server_name,url", SERVERS.items())
def test_initialize(server_name: str, url: str):
    """Handshake MCP deve retornar serverInfo e protocolVersion."""
    body = _initialize(url)
    assert "result" in body, f"[{server_name}] initialize sem 'result': {body}"
    result = body["result"]
    assert "serverInfo" in result,     f"[{server_name}] serverInfo ausente"
    assert "protocolVersion" in result, f"[{server_name}] protocolVersion ausente"


@pytest.mark.parametrize("server_name,url", SERVERS.items())
def test_tools_list(server_name: str, url: str):
    """tools/list deve expor pelo menos as ferramentas mínimas esperadas."""
    _initialize(url)
    tools = _tools_list(url)

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
    _initialize(url)
    tools = _tools_list(url)

    for tool in tools:
        name = tool.get("name", "<sem nome>")
        assert "name" in tool,        f"[{server_name}:{name}] campo 'name' ausente"
        assert "description" in tool, f"[{server_name}:{name}] campo 'description' ausente"
        assert "inputSchema" in tool, f"[{server_name}:{name}] campo 'inputSchema' ausente"

        schema = tool["inputSchema"]
        assert schema.get("type") == "object", (
            f"[{server_name}:{name}] inputSchema.type deve ser 'object', "
            f"recebido: {schema.get('type')}"
        )


@pytest.mark.parametrize("server_name,call", SMOKE_CALLS.items())
def test_tools_call_smoke(server_name: str, call: dict):
    """tools/call deve executar sem erro para inputs mínimos (sem DB)."""
    url = SERVERS[server_name]
    _initialize(url)

    result = _tools_call(url, call["name"], call["arguments"])
    assert result is not None, f"[{server_name}] tools/call retornou None"
    # Não valida conteúdo — apenas que o servidor respondeu sem jsonrpc error
