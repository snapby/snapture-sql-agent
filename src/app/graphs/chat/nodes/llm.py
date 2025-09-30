from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from anthropic import AsyncAnthropic
from anthropic.types.beta.beta_text_block import BetaTextBlock
from anthropic.types.beta.beta_thinking_block import BetaThinkingBlock
from anthropic.types.beta.beta_tool_use_block import BetaToolUseBlock
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import StreamWriter
from loguru import logger
from pydantic.json_schema import JsonSchemaValue

from app.graphs import Node
from app.utils import PromptStore

from ..state import ChatGraphState


def _get_block_display_type(content_block: Any) -> str:
    """Map content block type to display type.

    Attributes:
        content_block: The content block to map.

    Returns:
        The display type for the content block.
    """
    return (
        "tool-input"
        if content_block.type == "tool_use"
        else content_block.type
    )


class LLM(Node[ChatGraphState]):
    """Interacts with Anthropic models through Amazon Bedrock.

    Attributes:
        name: Identifier for the node in the graph.
    """

    name = "llm"

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        tool_schemas: dict[str, dict[str, str | JsonSchemaValue]],
        prompt_store: PromptStore,
    ) -> None:
        """Initializes the LLM node.

        Args:
            anthropic_client: Client for making LLM calls.
            tool_schemas: JSON schema for the tools available to the LLM.
            prompt_store: Store for managing prompts used in the graph.
        """
        self.anthropic_client = anthropic_client
        self.prompt_store = prompt_store
        self.tool_schemas = list(tool_schemas.values())
        self.tool_schemas[-1]["cache_control"] = {"type": "ephemeral"}

    def _validate_config(self, config: RunnableConfig) -> dict[str, Any]:
        """Validates and extracts node configuration.

        Args:
            config: Configuration for the node execution

        Returns:
            Validated node configuration

        Raises:
            KeyError: If required configuration is missing.
        """
        node_config = config.get("configurable", {}).get(self.name)
        if not node_config:
            raise KeyError(
                f"Configuration for node '{self.name}' is missing in 'configurable'."
            )

        required_keys = ["primary_model", "secondary_model", "tables"]
        for key in required_keys:
            if key not in node_config:
                raise KeyError(
                    f"'{key}' is required in the configuration for node '{self.name}'."
                )

        return node_config

    def _process_response_content(self, response: Any) -> list[dict[str, Any]]:
        """Processes response content blocks into serializable format.

        Args:
            response: The response message from the API

        Returns:
            List of processed content blocks

        Raises:
            ValueError: If the content block type is unexpected.
        """
        content: list[dict[str, Any]] = []
        should_exclude_text = (
            len(response.content) == 3
            and isinstance(response.content[0], BetaThinkingBlock)
            and isinstance(response.content[-1], BetaToolUseBlock)
        )

        for element in response.content:
            if isinstance(element, BetaThinkingBlock):
                content.append(element.model_dump())
            elif isinstance(element, BetaTextBlock):
                if not should_exclude_text:
                    content.append(element.model_dump(exclude={"citations"}))
            elif isinstance(element, BetaToolUseBlock):
                content.append(element.model_dump())
            else:
                logger.error(
                    "Unexpected content block type: {t}", t=type(element)
                )
                raise ValueError(
                    f"Unexpected content block type: {type(element)}"
                )

        return content

    @asynccontextmanager
    async def _stream_with_model(
        self,
        model_name: str,
        node_config: dict[str, Any],
        state: ChatGraphState,
    ) -> AsyncIterator[Any]:
        """Context manager for streaming with a specific model.

        Args:
            model_name: Name of the model to use
            node_config: Node configuration
            state: Current graph state

        Yields:
            Stream of messages from the model
        """

        # Prepare system prompt
        system_prompt_parts: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": f"<current_date> {datetime.now(timezone.utc).date()} </current_date>",
            },
            {
                "type": "text",
                "text": self.prompt_store.get_prompt("system.jinja2").render(
                    tables=node_config["tables"]
                ),
            },
        ]

        # Log detailed information about what we're sending to Anthropic
        logger.info(f"🚀 [LLM] Calling Anthropic API with model: {model_name}")
        logger.info(
            f"📊 [LLM] Max tokens: {node_config.get('max_tokens', 16_384)}"
        )
        logger.info(f"💬 [LLM] Messages count: {len(state.messages)}")
        logger.info(f"🔧 [LLM] Tools count: {len(self.tool_schemas)}")
        logger.info(
            f"📋 [LLM] System prompt parts count: {len(system_prompt_parts)}"
        )

        # Log messages being sent
        for i, msg in enumerate(state.messages):
            content_str = str(msg.get("content", ""))
            logger.info(
                f"📝 [LLM] Message {i}: role='{msg.get('role', 'unknown')}', content preview: '{content_str[:100]}{'...' if len(content_str) > 100 else ''}'"
            )
            # Log full message for debugging (truncated to avoid log spam)
            logger.debug(f"📋 [LLM] Full Message {i}: {msg}")

        # Log full conversation context for debugging
        logger.info(
            f"🔍 [LLM] Full conversation has {len(state.messages)} messages total"
        )
        if len(state.messages) > 1:
            logger.info(
                "🔄 [LLM] This appears to be a follow-up call with tool results"
            )

        # Log system prompt preview
        system_text = system_prompt_parts[1]["text"]
        logger.info(
            f"🎯 [LLM] System prompt preview (first 500 chars): {system_text[:500]}{'...' if len(system_text) > 500 else ''}"
        )

        # Log schema XML tables info if available
        if "tables" in node_config:
            tables_xml = node_config["tables"]
            logger.info(
                f"🗂️ [LLM] Tables XML length: {len(tables_xml)} characters"
            )
            if "<table" in tables_xml:
                table_count = tables_xml.count("<table")
                logger.info(
                    f"📊 [LLM] Number of tables in schema: {table_count}"
                )

        # Add cache control to the last system prompt part
        if isinstance(system_prompt_parts[-1], dict):
            system_prompt_parts[-1]["cache_control"] = {"type": "ephemeral"}

        logger.info(
            "⚡ [LLM] About to call Anthropic API - starting stream..."
        )

        # Add timeout and special handling for follow-up calls with tool results
        timeout_seconds = 60  # 1 minute timeout
        if len(state.messages) > 1:
            timeout_seconds = 90  # Longer timeout for follow-up calls
            logger.info(
                f"⏰ [LLM] Using extended timeout ({timeout_seconds}s) for follow-up call with tool results"
            )

        try:
            async with self.anthropic_client.beta.messages.stream(
                model=model_name,
                max_tokens=node_config.get("max_tokens", 16_384),
                thinking={"type": "enabled", "budget_tokens": 10_000},
                messages=state.messages,  # type: ignore
                tools=self.tool_schemas,  # type: ignore
                system=system_prompt_parts,  # type: ignore
                betas=["interleaved-thinking-2025-05-14"],
            ) as stream:
                logger.info("🌊 [LLM] Stream established successfully")
                yield stream
                logger.info("✅ [LLM] Stream completed successfully")

        except Exception as api_error:
            logger.error(
                f"💥 [LLM] Anthropic API error: {type(api_error).__name__}: {str(api_error)}"
            )
            logger.error(f"🔍 [LLM] Error details: {repr(api_error)}")
            raise

    async def _execute_with_model(
        self,
        model_name: str,
        node_config: dict[str, Any],
        state: ChatGraphState,
        writer: StreamWriter,
    ) -> ChatGraphState:
        """Execute LLM call with a specific model.

        Args:
            model_name: Name of the model to use
            node_config: Node configuration
            state: Current graph state
            writer: Stream writer for streaming custom events

        Returns:
            Updated graph state
        """
        async with self._stream_with_model(
            model_name=model_name, node_config=node_config, state=state
        ) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    writer(
                        {
                            "block-start": _get_block_display_type(
                                event.content_block
                            )
                        }
                    )

                elif event.type == "content_block_delta":
                    if event.delta.type == "thinking_delta":
                        writer({"thinking": event.delta.thinking})
                    elif event.delta.type == "text_delta":
                        writer({"text": event.delta.text})
                    elif event.delta.type == "input_json_delta":
                        writer({"tool-input": event.delta.partial_json})

                elif event.type == "content_block_stop":
                    writer(
                        {
                            "block-end": _get_block_display_type(
                                event.content_block
                            )
                        }
                    )

        response = await stream.get_final_message()
        content = self._process_response_content(response=response)

        return ChatGraphState(
            messages=[{"role": response.role, "content": content}],
            stop_reason=str(response.stop_reason),
            interrupt_policy=state.interrupt_policy,
        )

    async def __call__(
        self,
        state: ChatGraphState,
        config: RunnableConfig,
        writer: StreamWriter,
    ) -> ChatGraphState:
        """Invokes the LLM with fallback support.

        Args:
            state: Current state of the graph
            config: Configuration for the node execution
            writer: Stream writer for streaming custom events

        Returns:
            Updated graph state with new message and the llm stop reason.

        Raises:
            KeyError: If required configuration is missing.
            ValueError: If the content block type is unexpected.
            Exception: If both primary and fallback models fail.
        """
        node_config = self._validate_config(config=config)

        try:
            return await self._execute_with_model(
                model_name=node_config["primary_model"],
                node_config=node_config,
                state=state,
                writer=writer,
            )
        except Exception as primary_error:
            logger.warning(
                "Primary model `{model} failed with error: `{error}`.",
                model=node_config["primary_model"],
                error=str(primary_error),
            )

            try:
                return await self._execute_with_model(
                    model_name=node_config["secondary_model"],
                    node_config=node_config,
                    state=state,
                    writer=writer,
                )
            except Exception as fallback_error:
                logger.error(
                    "Both primary and fallback models failed. Primary model error: `{primary_error}`, Fallback model error: `{fallback_error}`.",
                    primary_error=str(primary_error),
                    fallback_error=str(fallback_error),
                )
                raise Exception(
                    f"Both models failed - Primary ({node_config['primary_model']}): {primary_error}, "
                    f"Fallback ({node_config['secondary_model']}): {fallback_error}"
                ) from fallback_error
