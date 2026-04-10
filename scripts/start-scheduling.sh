#!/bin/sh
exec uv run fastmcp run tools/interview_scheduling_server.py:mcp --transport streamable-http --host 0.0.0.0 --port 8004
