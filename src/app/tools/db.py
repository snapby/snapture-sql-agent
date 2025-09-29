import json
from typing import Annotated, Literal

import duckdb
from langgraph.types import interrupt
from loguru import logger
from pydantic import BaseModel, Field

from app.graphs.chat.state import ChatGraphState
from app.models.graph.interrupts import QueryExecutorHumanFeedback
from app.tools.base import BaseTool


class QueryExecutorInput(BaseModel):
    purpose: Annotated[
        Literal["intermediate", "final"],
        Field(
            description="Indicates the query's role in the workflow. "
            "'final' queries produce results that directly answer the user's "
            "question or query and are required for every response, "
            "'intermediate' queries are optional and used for data exploration "
            "or preparation before the final query."
        ),
    ]
    query: Annotated[
        str,
        Field(
            description="SQL query to execute against the database",
        ),
    ]


class QueryExecutorTool(
    BaseTool[ChatGraphState, QueryExecutorInput, str | dict],
    arbitrary_types_allowed=True,
):
    name: str = "duckdb_query_executor"
    description: str = "Executes a SQL query against a DuckDB database. DuckDB's SQL dialect is based on PostgreSQL"
    input_schema: type[QueryExecutorInput] = QueryExecutorInput

    conn: duckdb.DuckDBPyConnection

    async def __call__(
        self, input_data: QueryExecutorInput, state: ChatGraphState
    ) -> str | dict:
        should_interrupt = state.interrupt_policy == "always" or (
            state.interrupt_policy == "final" and input_data.purpose == "final"
        )
        query_modified = False
        human_reason = None

        if should_interrupt:
            human_feedback = interrupt(value=input_data.query)
            human_feedback = QueryExecutorHumanFeedback.model_validate(
                obj=human_feedback
            )

            if human_feedback.query != input_data.query:
                logger.debug("Human modified proposed query.")
                query_modified = True
                human_reason = human_feedback.reason
                input_data.query = human_feedback.query

        try:
            self.conn.execute(input_data.query)

            if self.conn.description is None:
                logger.info(
                    "Query executed successfully but returned no result set."
                )
                rows_affected = getattr(self.conn, "rowcount", None)
                return json.dumps(
                    dict(
                        message="Query executed successfully",
                        rows_affected=rows_affected,
                    ),
                    default=str,
                )

            columns = [desc[0] for desc in self.conn.description]
            rows = self.conn.fetchall()
            result = [dict(zip(columns, r)) for r in rows]
            logger.info("Query returned {n} rows.", n=len(result))

            # Limit results size for tool calls to prevent API timeout
            max_results = 50  # Limit to prevent large payloads
            truncated_result = result[:max_results]
            is_truncated = len(result) > max_results

            # Add summary for truncated results
            summary_info = {
                "total_rows": len(result),
                "returned_rows": len(truncated_result),
                "truncated": is_truncated,
            }

            # Return structured data instead of JSON string for better LLM processing
            if query_modified:
                return dict(
                    message="User modified the proposed query.",
                    executed_query=input_data.query,
                    reason=human_reason or "No reason provided.",
                    results=truncated_result,
                    summary=summary_info,
                )
            return dict(
                message="Query executed successfully",
                results=truncated_result,
                summary=summary_info,
            )

        except Exception as exc:
            code = str(exc.__class__)
            logger.exception(
                "There was an error executing the query.",
                exc=exc,
            )
            return json.dumps(
                {
                    "error": code,
                    "message": str(exc),
                },
                default=str,
            )
