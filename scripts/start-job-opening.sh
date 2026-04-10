#!/bin/sh
exec uv run fastmcp run tools/job_opening_server.py:mcp --transport streamable-http --host 0.0.0.0 --port 8001
