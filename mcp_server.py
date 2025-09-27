#!/usr/bin/env python3
"""Entry point for the MCP server.

This script serves as the main entry point for running the Snapture SQL Agent
as an MCP (Model Context Protocol) server. It can be used by MCP clients like
Claude Desktop to connect and use the SQL agent's capabilities.

Usage:
    python mcp_server.py

For Claude Desktop integration, add this to your claude_desktop_config.json:
{
  "mcpServers": {
    "snapture-sql-agent": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.mcp.config import get_mcp_config
from app.mcp.server import create_mcp_server


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Get server configuration (includes .env file loading)
        config = get_mcp_config()

        # Create and run the MCP server
        server = create_mcp_server(config)
        server.run()

    except KeyboardInterrupt:
        # Handle graceful shutdown
        print("MCP server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
