"""MCP server implementation for the Text-to-SQL Agent using FastMCP 2.0."""

import os
import tempfile
import xml.etree.ElementTree as ET
from typing import Annotated, Any, List
from urllib.parse import urlparse

import duckdb
import httpx
from anthropic import AsyncAnthropic
from fastmcp import FastMCP
from langsmith.wrappers import wrap_anthropic
from loguru import logger
from pydantic import Field

from app.graphs import create_chat_graph
from app.mcp.config import get_mcp_config
from app.tools import get_tool_handler
from app.tools.db import QueryExecutorTool
from app.utils import PromptStore

# Initialize the FastMCP server
mcp = FastMCP("Snapture SQL Agent")

# Global state for database connections and components
_db_connection: duckdb.DuckDBPyConnection | None = None
_query_executor: QueryExecutorTool | None = None
_anthropic_client: AsyncAnthropic | None = None
_chat_graph: Any = None
_tool_handler: Any = None
_prompt_store: Any = None


def _get_db_connection() -> duckdb.DuckDBPyConnection:
    """Get or create database connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = duckdb.connect(":memory:")
    return _db_connection


def _get_query_executor() -> QueryExecutorTool:
    """Get or create query executor."""
    global _query_executor
    if _query_executor is None:
        _query_executor = QueryExecutorTool(conn=_get_db_connection())
    return _query_executor


def _initialize_chat_components() -> None:
    """Initialize components needed for chat functionality."""
    global _anthropic_client, _chat_graph, _tool_handler, _prompt_store

    # Always re-initialize tool handler and chat graph to pick up latest DB state
    if _anthropic_client is None:
        # Get config first (this loads .env file)
        config = get_mcp_config()

        # Now check for API key (after .env is loaded)
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for chat functionality. "
                "Please set it in your .env file or environment. "
                "Get your API key at: https://console.anthropic.com/"
            )

        # Initialize Anthropic client (only once)
        _anthropic_client = wrap_anthropic(
            client=AsyncAnthropic(api_key=anthropic_api_key)
        )

        # Initialize prompt store (only once)
        _prompt_store = PromptStore(
            prompts_dir=config.app_settings.paths.prompts_dir
        )

    # Always re-initialize tool handler to pick up latest database state
    _tool_handler = get_tool_handler(
        dependencies={"conn": _get_db_connection()}
    )

    # Always re-create chat graph with fresh tool handler
    _chat_graph = create_chat_graph(
        anthropic_client=_anthropic_client,
        tool_handler=_tool_handler,
        prompt_store=_prompt_store,
        checkpointer=None,  # No checkpointer for MCP server
    )


def _generate_tables_schema_xml() -> str:
    """Generate tables schema in XML format for LangGraph configuration."""
    try:
        db_connection = _get_db_connection()

        # Get all tables
        tables_result = db_connection.execute("SHOW TABLES").fetchall()

        if not tables_result:
            return "<tables_schema></tables_schema>"

        # Build schemas structure
        schemas = []
        for table_row in tables_result:
            table_name = table_row[0]

            # Get column info for this table
            cols = db_connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            # Format schema as expected by the XML function
            schema = [{c[1]: c[2]} for c in cols]  # {column_name: data_type}
            schemas.append({"table_name": table_name, "schema": schema})

        # Generate XML using the same function as FastAPI
        root = ET.Element("tables_schema")
        for tbl in schemas:
            table_el = ET.SubElement(
                root, "table", {"name": tbl["table_name"]}
            )
            for col in tbl.get("schema", []):
                ((col_name, data_type),) = col.items()
                ET.SubElement(
                    table_el,
                    "column",
                    {"name": col_name, "data_type": data_type},
                )

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        return ET.tostring(root, encoding="unicode")

    except Exception as e:
        logger.error(f"Error generating tables schema XML: {e}")
        return "<tables_schema></tables_schema>"


def _upload_csv_helper(
    csv_content: str, table_name: str, description: str = ""
) -> str:
    """Helper function to upload CSV data to DuckDB (not a tool)."""
    db_connection = _get_db_connection()

    # Write CSV content to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        f.write(csv_content)
        temp_file = f.name

    try:
        # Load CSV into DuckDB
        db_connection.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv('{temp_file}', auto_detect=true, header=true)
        """)

        # Get table schema
        schema_result = db_connection.execute(
            f"DESCRIBE {table_name}"
        ).fetchall()
        schema_info = []
        for row in schema_result:
            schema_info.append(f"  {row[0]}: {row[1]}")

        schema_text = "\\n".join(schema_info)

        # Get row count
        row_count_result = db_connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()
        row_count = row_count_result[0] if row_count_result else 0

        return f"""CSV data successfully uploaded!

Table: {table_name}
Rows: {row_count}
Description: {description or "No description provided"}

Schema:
{schema_text}

The data is now ready for SQL queries. Use the execute_sql_query tool to analyze it!"""

    finally:
        # Clean up temp file
        os.unlink(temp_file)


# @mcp.tool
# async def execute_sql_query(
#     query: Annotated[
#         str,
#         Field(
#             description="SQL query to execute against the uploaded CSV data"
#         ),
#     ],
#     purpose: Annotated[
#         str,
#         Field(
#             description="Purpose of query: 'intermediate' for exploration, 'final' for results",
#             default="final",
#         ),
#     ],
# ) -> str:
#     """Execute SQL query against the DuckDB database containing uploaded CSV data."""
#     query_executor = _get_query_executor()
#
#     try:
#         # Create a mock state for the query executor
#         mock_state = type("MockState", (), {"interrupt_policy": "never"})()
#
#         # Create input data for the tool
#         input_data = type(
#             "QueryInput", (), {"query": query, "purpose": purpose}
#         )()
#
#         result = await query_executor(input_data, mock_state)
#         return f"SQL Query Results:\\n{result}"
#
#     except Exception as e:
#         logger.error(f"Error executing SQL query: {e}")
#         raise Exception(f"Error executing query: {str(e)}")


# @mcp.tool
# async def upload_csv_data(
#     csv_content: Annotated[
#         str, Field(description="CSV data as string content")
#     ],
#     table_name: Annotated[
#         str,
#         Field(description="Name for the table to create from the CSV data"),
#     ],
#     description: Annotated[
#         str, Field(description="Optional description of the data", default="")
#     ] = "",
# ) -> str:
#     """Upload CSV data to DuckDB and make it available for querying."""
#     try:
#         return _upload_csv_helper(csv_content, table_name, description)
#     except Exception as e:
#         logger.error(f"Error uploading CSV data: {e}")
#         raise Exception(f"Error uploading CSV data: {str(e)}")


@mcp.tool
async def upload_csv_from_url(
    url: Annotated[str, Field(description="URL to fetch CSV data from")],
    table_name: Annotated[
        str,
        Field(description="Name for the table to create from the CSV data"),
    ],
    description: Annotated[
        str, Field(description="Optional description of the data", default="")
    ] = "",
) -> str:
    """Fetch CSV data from a URL and upload it to DuckDB."""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise Exception("Invalid URL provided")

        # Fetch CSV data
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            csv_content = response.text

        # Use the helper function to upload CSV
        result = _upload_csv_helper(
            csv_content, table_name, f"Data from {url}. {description}"
        )
        return result

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching CSV from URL: {e}")
        raise Exception(f"Error fetching CSV from URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error uploading CSV from URL: {e}")
        raise Exception(f"Error uploading CSV from URL: {str(e)}")


@mcp.tool
async def get_database_schema() -> str:
    """Get the current database schema showing all available tables and their structures."""
    try:
        db_connection = _get_db_connection()

        # Get all tables
        tables_result = db_connection.execute("SHOW TABLES").fetchall()

        if not tables_result:
            return "No tables found in the database. Upload CSV data first using the upload_csv_data tool."

        schema_info = ["Database Schema:", "=" * 50]

        for table_row in tables_result:
            table_name = table_row[0]
            schema_info.append(f"\\nTable: {table_name}")
            schema_info.append("-" * (len(table_name) + 7))

            # Get table schema
            table_schema = db_connection.execute(
                f"DESCRIBE {table_name}"
            ).fetchall()
            for col_row in table_schema:
                schema_info.append(f"  {col_row[0]}: {col_row[1]}")

            # Get row count
            row_count_result = db_connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()
            row_count = row_count_result[0] if row_count_result else 0
            schema_info.append(f"  Rows: {row_count}")

        return "\\n".join(schema_info)

    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        raise Exception(f"Error getting database schema: {str(e)}")


@mcp.tool
async def chat_with_data(
    question: Annotated[
        str, Field(description="Your question about the data")
    ],
) -> str:
    """Have a conversational chat about your data using natural language."""
    # Ensure query executor is available
    _ = _get_query_executor()  # Initialize if needed

    # Initialize chat components after ensuring DB is ready
    _initialize_chat_components()

    try:
        # Generate tables schema XML for LangGraph configuration
        tables_schema_xml = _generate_tables_schema_xml()
        logger.info(
            f"📊 Generated tables schema XML: {len(tables_schema_xml)} characters"
        )

        # Configure proper LangGraph config as expected by LLM node
        config = {
            "configurable": {
                "llm": {
                    "primary_model": "claude-sonnet-4-20250514",
                    "secondary_model": "claude-opus-4-1-20250805",
                    "max_tokens": 16384,
                    "tables": tables_schema_xml,
                }
            },
            "recursion_limit": 50,
        }

        # Execute the chat graph with proper configuration
        # Convert question to messages format as expected by ChatGraphState
        input_data = {
            "messages": [{"role": "user", "content": question}],
            "interrupt_policy": "never",
        }

        logger.info(
            f"🤖 Starting chat with question: '{question[:100]}{'...' if len(question) > 100 else ''}'"
        )
        logger.info(
            f"📋 LangGraph config: primary_model={config['configurable']['llm']['primary_model']}, max_tokens={config['configurable']['llm']['max_tokens']}"  # type: ignore
        )
        logger.info(f"📝 Input data: {input_data}")
        logger.info(
            f"🗂️ Tables schema preview: {tables_schema_xml[:500]}{'...' if len(tables_schema_xml) > 500 else ''}"
        )

        # Set debug logging for more detailed message tracing
        import os

        if os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes"):
            logger.info("🔍 [DEBUG MODE] Full input data:")
            logger.info(f"📋 [DEBUG] {input_data}")
            logger.info("🔍 [DEBUG MODE] Full tables schema:")
            logger.info(f"📋 [DEBUG] {tables_schema_xml}")

        logger.info("⏳ [CHAT] Executing chat graph...")
        result = await _chat_graph.ainvoke(input_data, config)
        logger.info(
            f"✅ [CHAT] Chat graph execution completed. Result type: {type(result)}"
        )

        # Extract the response
        if isinstance(result, dict) and "response" in result:
            response = result["response"]
            if hasattr(response, "content"):
                response_text = str(response.content)
                logger.info(
                    f"📤 [CHAT] Response extracted from result.response.content: {len(response_text)} characters"
                )
                return response_text
            response_text = str(response)
            logger.info(
                f"📤 [CHAT] Response extracted from result.response: {len(response_text)} characters"
            )
            return response_text

        response_text = str(result)
        logger.info(
            f"📤 [CHAT] Response from raw result: {len(response_text)} characters"
        )
        return response_text

    except Exception as e:
        logger.error(f"Error in chat_with_data: {e}")
        raise Exception(f"Error processing your question: {str(e)}")


# @mcp.tool
# async def chat_with_data_stream(
#     question: Annotated[
#         str, Field(description="Your question about the data")
#     ],
#     include_thinking: Annotated[
#         bool,
#         Field(
#             description="Whether to include AI thinking process", default=False
#         ),
#     ] = False,
# ) -> List[str]:
#     """Have a conversational chat about your data with streaming response chunks."""
#     # Ensure query executor is available
#     _ = _get_query_executor()  # Initialize if needed
#
#     # Initialize chat components after ensuring DB is ready
#     _initialize_chat_components()
#
#     try:
#         streaming_chunks = []
#         current_content = ""
#         last_yielded_length = 0
#
#         # Generate tables schema XML for LangGraph configuration
#         tables_schema_xml = _generate_tables_schema_xml()
#         logger.info(
#             f"📊 [STREAM] Generated tables schema XML: {len(tables_schema_xml)} characters"
#         )
#
#         # Configure proper LangGraph config as expected by LLM node
#         config = {
#             "configurable": {
#                 "llm": {
#                     "primary_model": "claude-sonnet-4-20250514",
#                     "secondary_model": "claude-opus-4-1-20250805",
#                     "max_tokens": 16384,
#                     "tables": tables_schema_xml,
#                 }
#             },
#             "recursion_limit": 50,
#         }
#
#         # Stream from the chat graph with proper configuration
#         # Convert question to messages format as expected by ChatGraphState
#         input_data = {
#             "messages": [{"role": "user", "content": question}],
#             "interrupt_policy": "never",
#         }
#
#         logger.info(
#             f"🔄 [STREAM] Starting streaming chat with question: '{question[:100]}{'...' if len(question) > 100 else ''}'"
#         )
#         logger.info(
#             f"📋 [STREAM] LangGraph config: primary_model={config['configurable']['llm']['primary_model']}"  # type: ignore
#         )
#         logger.info(
#             f"🗂️ [STREAM] Tables schema preview: {tables_schema_xml[:500]}{'...' if len(tables_schema_xml) > 500 else ''}"
#         )
#
#         async for event in _chat_graph.astream(input_data, config):
#             if isinstance(event, dict):
#                 for node_name, node_data in event.items():
#                     if node_name == "generate" and isinstance(node_data, dict):
#                         if "response" in node_data:
#                             response = node_data["response"]
#
#                             # Handle different response types
#                             if hasattr(response, "content"):
#                                 new_content = str(response.content)
#                             elif isinstance(response, str):
#                                 new_content = response
#                             else:
#                                 new_content = str(response)
#
#                             # Check for new content to yield
#                             if len(new_content) > last_yielded_length:
#                                 delta = new_content[last_yielded_length:]
#                                 if delta.strip():  # Only add non-empty chunks
#                                     streaming_chunks.append(delta)
#                                     last_yielded_length = len(new_content)
#                             current_content = new_content
#
#                     # Include thinking/debug streams if requested
#                     elif include_thinking and node_name in [
#                         "search",
#                         "analyze",
#                         "query",
#                     ]:
#                         if isinstance(node_data, dict):
#                             thinking_text = (
#                                 f"[{node_name.upper()}] {str(node_data)}"
#                             )
#                             streaming_chunks.append(thinking_text)
#
#         # If no streaming chunks collected but we have final content
#         if not streaming_chunks and current_content:
#             streaming_chunks.append(current_content)
#         elif not streaming_chunks and not current_content:
#             streaming_chunks.append(
#                 "✅ I processed your request, but didn't generate a specific response. Please try rephrasing your question."
#             )
#
#         return (
#             streaming_chunks
#             if streaming_chunks
#             else ["✅ Chat completed successfully."]
#         )
#
#     except Exception as e:
#         logger.error(f"Error in chat_with_data_stream: {e}")
#         raise Exception(
#             f"Error during streaming chat: {str(e)}. Please make sure you have uploaded CSV data first."
#         )


if __name__ == "__main__":
    mcp.run()
