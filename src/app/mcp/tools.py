"""MCP tool wrappers for existing SQL agent tools.

This module provides MCP-compatible wrappers around the existing tool implementations,
allowing them to be used within the MCP server context.
"""

from typing import List

import duckdb
from loguru import logger
from mcp.types import TextContent

from app.tools.db import QueryExecutorInput, QueryExecutorTool


class MCPQueryExecutor:
    """MCP-compatible wrapper for the SQL query executor."""

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        """Initialize the MCP query executor.

        Args:
            connection: DuckDB database connection
        """
        self.query_tool = QueryExecutorTool(conn=connection)
        self.connection = connection

    async def execute_query(
        self, query: str, purpose: str = "final"
    ) -> List[TextContent]:
        """Execute a SQL query and return MCP-formatted results.

        Args:
            query: SQL query to execute
            purpose: Query purpose ('intermediate' or 'final')

        Returns:
            List of TextContent with query results
        """
        try:
            # Create input for the query executor
            query_input = QueryExecutorInput(query=query, purpose=purpose)

            # Create a mock state (since we're running standalone)
            mock_state = type("MockState", (), {"interrupt_policy": "never"})()

            # Execute the query using the existing tool
            result = await self.query_tool(query_input, mock_state)

            return [TextContent(type="text", text=f"Query Results:\n{result}")]

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return [
                TextContent(
                    type="text", text=f"Error executing query: {str(e)}"
                )
            ]


class MCPSchemaInspector:
    """MCP-compatible tool for inspecting database schema."""

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        """Initialize the schema inspector.

        Args:
            connection: DuckDB database connection
        """
        self.connection = connection

    async def get_all_tables(self) -> List[TextContent]:
        """Get information about all available tables.

        Returns:
            List of TextContent with table information
        """
        try:
            tables = self.connection.execute("SHOW TABLES").fetchall()

            if not tables:
                return [
                    TextContent(
                        type="text",
                        text="No tables found in the database. Please upload CSV data first.",
                    )
                ]

            table_info = []
            for table_row in tables:
                table_name = table_row[0]
                try:
                    row_count = self.connection.execute(
                        f"SELECT COUNT(*) FROM {table_name}"
                    ).fetchone()[0]
                    table_info.append(f"• {table_name} ({row_count} rows)")
                except Exception as e:
                    table_info.append(
                        f"• {table_name} (error counting rows: {e})"
                    )

            return [
                TextContent(
                    type="text",
                    text="Available tables:\n" + "\n".join(table_info),
                )
            ]

        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return [
                TextContent(
                    type="text", text=f"Error retrieving table list: {str(e)}"
                )
            ]

    async def get_table_schema(self, table_name: str) -> List[TextContent]:
        """Get detailed schema for a specific table.

        Args:
            table_name: Name of the table to inspect

        Returns:
            List of TextContent with schema information
        """
        try:
            # Check if table exists
            tables = self.connection.execute("SHOW TABLES").fetchall()
            table_names = [row[0] for row in tables]

            if table_name not in table_names:
                return [
                    TextContent(
                        type="text",
                        text=f"Table '{table_name}' not found. Available tables: {', '.join(table_names)}",
                    )
                ]

            # Get schema information
            schema = self.connection.execute(
                f"DESCRIBE {table_name}"
            ).fetchall()
            row_count = self.connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            # Format schema information
            schema_lines = []
            for column_info in schema:
                col_name, col_type, null_info = (
                    column_info[0],
                    column_info[1],
                    column_info[2],
                )
                null_text = "NULL" if null_info == "YES" else "NOT NULL"
                schema_lines.append(f"  {col_name}: {col_type} ({null_text})")

            schema_text = f"""Table: {table_name}
Rows: {row_count}

Columns:
{chr(10).join(schema_lines)}

Sample query: SELECT * FROM {table_name} LIMIT 5;"""

            return [TextContent(type="text", text=schema_text)]

        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error retrieving schema for table '{table_name}': {str(e)}",
                )
            ]


class MCPCSVUploader:
    """MCP-compatible tool for uploading and processing CSV data."""

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        """Initialize the CSV uploader.

        Args:
            connection: DuckDB database connection
        """
        self.connection = connection

    async def upload_csv_content(
        self, csv_content: str, table_name: str, description: str = ""
    ) -> List[TextContent]:
        """Upload CSV content to DuckDB.

        Args:
            csv_content: Raw CSV data as string
            table_name: Name for the new table
            description: Optional description of the data

        Returns:
            List of TextContent with upload results
        """
        try:
            import os
            import tempfile

            # Validate table name (basic SQL injection prevention)
            if not table_name.isidentifier():
                return [
                    TextContent(
                        type="text",
                        text=f"Invalid table name: '{table_name}'. Table names must be valid SQL identifiers.",
                    )
                ]

            # Write CSV to temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as temp_file:
                temp_file.write(csv_content)
                temp_path = temp_file.name

            try:
                # Load CSV into DuckDB
                self.connection.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS 
                    SELECT * FROM read_csv('{temp_path}', auto_detect=true, header=true)
                """)

                # Get information about the loaded table
                row_count = self.connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]
                schema = self.connection.execute(
                    f"DESCRIBE {table_name}"
                ).fetchall()

                # Format schema information
                schema_lines = []
                for column_info in schema:
                    col_name, col_type = column_info[0], column_info[1]
                    schema_lines.append(f"  {col_name}: {col_type}")

                success_message = f"""✅ CSV data uploaded successfully!

Table: {table_name}
Rows loaded: {row_count}
Description: {description or "No description provided"}

Schema:
{chr(10).join(schema_lines)}

The table is now available for querying. Use execute_sql_query to run SQL queries against this data."""

                return [TextContent(type="text", text=success_message)]

            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Error uploading CSV data: {e}")
            return [
                TextContent(
                    type="text", text=f"❌ Error uploading CSV data: {str(e)}"
                )
            ]
