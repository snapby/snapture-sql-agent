"""MCP server configuration."""

from functools import lru_cache

from pydantic import BaseModel, Field

from app.config import Settings, get_settings


class MCPServerConfig(BaseModel):
    """Configuration for the MCP server."""

    server_name: str = Field(
        default="snapture-sql-agent", description="Name of the MCP server"
    )
    server_version: str = Field(
        default="1.0.0", description="Version of the MCP server"
    )
    description: str = Field(
        default="MCP server for Text-to-SQL agent with DuckDB integration",
        description="Description of the MCP server",
    )

    # Main application settings (loaded from .env file)
    app_settings: Settings = Field(
        description="Main application settings including database, API keys, etc."
    )

    # CSV upload directory
    csv_upload_dir: str = Field(
        default="./uploads",
        description="Directory where CSV files are temporarily stored",
    )

    # Maximum file size for uploads (in bytes)
    max_file_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Maximum size for CSV file uploads",
    )

    class Config:
        """Pydantic config."""

        extra = "forbid"


@lru_cache(maxsize=1)
def get_mcp_config() -> MCPServerConfig:
    """Get MCP server configuration with main application settings."""
    app_settings = get_settings()

    return MCPServerConfig(
        app_settings=app_settings,
        server_name="snapture-sql-agent",
        server_version="1.0.0",
        description="MCP server for Text-to-SQL agent with DuckDB and CSV integration",
    )
