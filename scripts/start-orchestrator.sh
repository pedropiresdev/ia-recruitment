#!/bin/sh
exec uv run fastmcp run tools/recruitment_orchestrator_server.py:mcp --transport streamable-http --host 0.0.0.0 --port 8000
