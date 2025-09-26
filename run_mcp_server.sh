#!/bin/bash
# Script helper para executar o servidor MCP com uv
# Usado pelo MCP Inspector e outros clientes MCP

export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
exec uv run python mcp_server.py