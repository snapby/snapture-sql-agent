"""MCP (Model Context Protocol) server implementation for the Text-to-SQL Agent.

This module provides MCP server functionality that exposes the SQL agent's
capabilities as standardized MCP tools, allowing AI applications like Claude Desktop
to connect and use the agent's text-to-SQL capabilities.
"""

from .server import create_mcp_server

__all__ = ["create_mcp_server"]
