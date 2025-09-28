#!/usr/bin/env python3
"""Entry point for the MCP server.

This script serves as the main entry point for running the Snapture SQL Agent
as an MCP (Model Context Protocol) server. It supports both stdio mode for
MCP client integration and HTTP mode for web-based testing.

Usage:
    python mcp_server.py                    # STDIO mode (default)
    python mcp_server.py --http             # HTTP mode with web interface
    python mcp_server.py --http --port 8080 # HTTP mode on custom port

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
Opens a web interface at http://localhost:3000 where you can test the MCP tools
directly in your browser. Useful for development and testing.
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.mcp.config import get_mcp_config
from app.mcp.server import create_mcp_server


def main() -> None:
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Snapture SQL Agent MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_server.py                    # STDIO mode (default)
  python mcp_server.py --http             # HTTP mode on localhost:3000
  python mcp_server.py --http --port 8080 # HTTP mode on localhost:8080
  python mcp_server.py --http --host 0.0.0.0 --port 9000  # HTTP mode accessible from any IP
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
        # Get server configuration (includes .env file loading)
        config = get_mcp_config()

        # Create and run the MCP server
        server = create_mcp_server(config)

        if args.http:
            server.run(transport="http", host=args.host, port=args.port)
        else:
            server.run(transport="stdio")

    except KeyboardInterrupt:
        # Handle graceful shutdown
        print("\nMCP server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
