"""MCP server configuration."""

from typing import Any

from pydantic import BaseModel, Field


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

    # Database connection settings (will be passed from main app settings)
    database_config: dict[str, Any] = Field(
        default_factory=dict, description="Database configuration settings"
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
