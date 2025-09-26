"""MCP server implementation for the Text-to-SQL Agent."""

import asyncio
from typing import List

import duckdb
from loguru import logger
from mcp import FastMCP, McpError
from mcp.types import TextContent

from app.mcp.config import MCPServerConfig
from app.tools.db import QueryExecutorTool


class SQLAgentMCPServer:
    """MCP server that exposes SQL agent functionality."""

    def __init__(self, config: MCPServerConfig):
        """Initialize the MCP server.

        Args:
            config: Server configuration
        """
        self.config = config
        self.mcp = FastMCP(
            name=config.server_name,
            version=config.server_version,
            description=config.description,
        )
        self.db_connection: duckdb.DuckDBPyConnection | None = None
        self.query_executor: QueryExecutorTool | None = None

        # Register MCP tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tools."""

        @self.mcp.tool(
            name="execute_sql_query",
            description="Execute SQL query against the DuckDB database containing uploaded CSV data",
        )
        async def execute_sql_query(
            query: str, purpose: str = "final"
        ) -> List[TextContent]:
            """Execute a SQL query.

            Args:
                query: SQL query to execute
                purpose: Purpose of query - 'intermediate' for exploration, 'final' for results

            Returns:
                Query results as text content
            """
            if not self.query_executor:
                raise McpError(
                    "Database not initialized. Please upload CSV data first."
                )

            try:
                # Create a mock state for the query executor
                mock_state = type(
                    "MockState", (), {"interrupt_policy": "never"}
                )()

                # Create input data for the tool
                input_data = type(
                    "QueryInput", (), {"query": query, "purpose": purpose}
                )()

                result = await self.query_executor(input_data, mock_state)

                return [
                    TextContent(
                        type="text", text=f"SQL Query Results:\n{result}"
                    )
                ]

            except Exception as e:
                logger.error(f"Error executing SQL query: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error executing query: {str(e)}"
                    )
                ]

        @self.mcp.tool(
            name="upload_csv_data",
            description="Upload CSV data and make it available for querying",
        )
        async def upload_csv_data(
            csv_content: str, table_name: str, description: str = ""
        ) -> List[TextContent]:
            """Upload CSV data to DuckDB.

            Args:
                csv_content: CSV data as string
                table_name: Name for the table to create
                description: Optional description of the data

            Returns:
                Success message with table schema information
            """
            try:
                # Initialize database connection if needed
                if not self.db_connection:
                    self.db_connection = duckdb.connect(":memory:")
                    self.query_executor = QueryExecutorTool(
                        conn=self.db_connection
                    )

                # Write CSV content to temporary file
                import os
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as f:
                    f.write(csv_content)
                    temp_file = f.name

                try:
                    # Load CSV into DuckDB
                    self.db_connection.execute(f"""
                        CREATE OR REPLACE TABLE {table_name} AS 
                        SELECT * FROM read_csv('{temp_file}', auto_detect=true, header=true)
                    """)

                    # Get table schema
                    schema_result = self.db_connection.execute(
                        f"DESCRIBE {table_name}"
                    ).fetchall()
                    schema_info = []
                    for row in schema_result:
                        schema_info.append(f"  {row[0]}: {row[1]}")

                    schema_text = "\n".join(schema_info)

                    # Get row count
                    row_count = self.db_connection.execute(
                        f"SELECT COUNT(*) FROM {table_name}"
                    ).fetchone()[0]

                    success_message = f"""CSV data successfully uploaded!

Table: {table_name}
Rows: {row_count}
Description: {description or "No description provided"}

Schema:
{schema_text}

You can now query this data using execute_sql_query tool."""

                    return [TextContent(type="text", text=success_message)]

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)

            except Exception as e:
                logger.error(f"Error uploading CSV data: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error uploading CSV data: {str(e)}"
                    )
                ]

        @self.mcp.tool(
            name="get_table_schema",
            description="Get schema information for available tables",
        )
        async def get_table_schema(table_name: str = "") -> List[TextContent]:
            """Get schema information for tables.

            Args:
                table_name: Specific table name, or empty to get all tables

            Returns:
                Schema information
            """
            if not self.db_connection:
                return [
                    TextContent(
                        type="text",
                        text="No database connection. Please upload CSV data first.",
                    )
                ]

            try:
                if table_name:
                    # Get schema for specific table
                    schema_result = self.db_connection.execute(
                        f"DESCRIBE {table_name}"
                    ).fetchall()
                    row_count = self.db_connection.execute(
                        f"SELECT COUNT(*) FROM {table_name}"
                    ).fetchone()[0]

                    schema_info = []
                    for row in schema_result:
                        schema_info.append(f"  {row[0]}: {row[1]}")

                    schema_text = f"""Table: {table_name}
Rows: {row_count}

Schema:
{chr(10).join(schema_info)}"""
                else:
                    # Get all tables
                    tables_result = self.db_connection.execute(
                        "SHOW TABLES"
                    ).fetchall()
                    if not tables_result:
                        schema_text = "No tables available. Please upload CSV data first."
                    else:
                        table_info = []
                        for table_row in tables_result:
                            table = table_row[0]
                            row_count = self.db_connection.execute(
                                f"SELECT COUNT(*) FROM {table}"
                            ).fetchone()[0]
                            table_info.append(f"  {table} ({row_count} rows)")

                        schema_text = f"""Available tables:
{chr(10).join(table_info)}

Use get_table_schema with a specific table name for detailed schema information."""

                return [TextContent(type="text", text=schema_text)]

            except Exception as e:
                logger.error(f"Error getting table schema: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error getting schema: {str(e)}"
                    )
                ]

        @self.mcp.tool(
            name="list_available_tables",
            description="List all available tables in the database",
        )
        async def list_available_tables() -> List[TextContent]:
            """List all available tables.

            Returns:
                List of available tables
            """
            if not self.db_connection:
                return [
                    TextContent(
                        type="text",
                        text="No database connection. Please upload CSV data first.",
                    )
                ]

            try:
                tables_result = self.db_connection.execute(
                    "SHOW TABLES"
                ).fetchall()
                if not tables_result:
                    return [
                        TextContent(
                            type="text",
                            text="No tables available. Please upload CSV data using upload_csv_data tool.",
                        )
                    ]

                table_list = []
                for table_row in tables_result:
                    table_name = table_row[0]
                    row_count = self.db_connection.execute(
                        f"SELECT COUNT(*) FROM {table_name}"
                    ).fetchone()[0]
                    table_list.append(f"• {table_name} ({row_count} rows)")

                tables_text = f"""Available tables:
{chr(10).join(table_list)}

Use get_table_schema to see detailed schema information for any table.
Use execute_sql_query to query the data."""

                return [TextContent(type="text", text=tables_text)]

            except Exception as e:
                logger.error(f"Error listing tables: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error listing tables: {str(e)}"
                    )
                ]

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting MCP server: {self.config.server_name}")
        await self.mcp.run(transport="stdio")


def create_mcp_server(config: MCPServerConfig) -> SQLAgentMCPServer:
    """Create and configure MCP server.

    Args:
        config: Server configuration

    Returns:
        Configured MCP server instance
    """
    return SQLAgentMCPServer(config)


async def main() -> None:
    """Main entry point for running the MCP server directly."""
    config = MCPServerConfig()
    server = create_mcp_server(config)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
