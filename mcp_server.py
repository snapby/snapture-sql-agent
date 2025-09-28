#!/usr/bin/env python3
"""Entry point for the MCP server using FastMCP 2.0.

This script serves as the main entry point for running the Snapture SQL Agent
as an MCP (Model Context Protocol) server using FastMCP 2.0. It supports both
stdio mode for MCP client integration and HTTP mode for web-based testing.

Usage:
    python mcp_server.py                    # STDIO mode (default)
    python mcp_server.py --http             # HTTP mode with web interface
    python mcp_server.py --http --port 8080 # HTTP mode on custom port

    # Or using FastMCP CLI:
    fastmcp run mcp_server.py:mcp           # STDIO mode
    fastmcp run mcp_server.py:mcp --transport http --port 8080  # HTTP mode

STDIO Mode (MCP Integration):
For Claude Desktop integration, add this to your claude_desktop_config.json:
{
  "mcpServers": {
    "snapture-sql-agent": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}

HTTP Mode (Web Testing):
Opens a web interface where you can test the MCP tools directly in your browser.
Useful for development and testing.
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the FastMCP server instance
from app.mcp.server import mcp


def main() -> None:
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Snapture SQL Agent MCP Server (FastMCP 2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_server.py                    # STDIO mode (default)
  python mcp_server.py --http             # HTTP mode on localhost:3000
  python mcp_server.py --http --port 8080 # HTTP mode on localhost:8080
  
  # Using FastMCP CLI (recommended):
  fastmcp run mcp_server.py:mcp           # STDIO mode
  fastmcp run mcp_server.py:mcp --transport http --port 8080  # HTTP mode
        """,
    )

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode with web interface (default: stdio mode)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to in HTTP mode (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to bind to in HTTP mode (default: 3000)",
    )

    args = parser.parse_args()

    try:
        # Run the MCP server with the requested transport
        if args.http:
            mcp.run(transport="http", host=args.host, port=args.port)
        else:
            mcp.run(transport="stdio")

    except KeyboardInterrupt:
        # Handle graceful shutdown
        print("\nMCP server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
