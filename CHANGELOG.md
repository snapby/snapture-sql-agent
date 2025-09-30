# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-09-30

### 🚀 Features

- Add MCP (Model Context Protocol) server integration ([f21b756](../../commit/f21b756))
- Add upload_csv_from_url MCP tool ([07aabab](../../commit/07aabab))
- Add MCP Inspector support and testing infrastructure ([840a6f6](../../commit/840a6f6))
- Add chat_with_data tool to MCP server ([a760f9e](../../commit/a760f9e))
- Add streaming chat functionality to MCP server ([a90da88](../../commit/a90da88))
- add HTTP mode support with STDIO fallback ([d5c5cc1](../../commit/d5c5cc1))
- migrate to FastMCP 2.0 with native HTTP support ([6f25d34](../../commit/6f25d34))
- add comprehensive debug logging for chat system ([9ee1bf9](../../commit/9ee1bf9))
- enhanced debug logging for timeout diagnosis ([85627c3](../../commit/85627c3))
- add comprehensive release management system with changelog generation ([a1a5a78](../../commit/a1a5a78))

### 🐛 Bug Fixes

- Correct FastMCP initialization parameters ([f09e5d5](../../commit/f09e5d5))
- Resolve asyncio 'Already running asyncio in this thread' error ([a1d21b5](../../commit/a1d21b5))
- resolve 'FunctionTool' object not callable error in CSV upload ([81933d0](../../commit/81933d0))
- resolve database initialization error in chat tools ([895f0ff](../../commit/895f0ff))
- ensure chat tools see latest database state in HTTP mode ([15d77f1](../../commit/15d77f1))
- resolve LangGraph LLM node configuration error ([32708ca](../../commit/32708ca))
- implement proper Anthropic API key configuration and validation ([68283bf](../../commit/68283bf))
- load .env file before checking ANTHROPIC_API_KEY ([c38105c](../../commit/c38105c))
- correct chat graph input format to match ChatGraphState ([11a0557](../../commit/11a0557))
- resolve mypy type errors across the codebase ([33360db](../../commit/33360db))

### 🧹 Maintenance

- chore: update package dependencies ([59ce2f0](../../commit/59ce2f0))

### 🔧 Other Changes

- first commit ([14106bd](../../commit/14106bd))
- Merge pull request #1 from snapby/feature/mcp-server-integration ([57dfb19](../../commit/57dfb19))
- Merge pull request #2 from snapby/feature/mcp-server-integration ([5a914d1](../../commit/5a914d1))
- Merge pull request #3 from snapby/feature/mcp-server-integration ([0b1609b](../../commit/0b1609b))
- Merge pull request #4 from snapby/feature/mcp-server-integration ([1486ffc](../../commit/1486ffc))
- Merge pull request #5 from snapby/feature/mcp-server-integration ([29fe69b](../../commit/29fe69b))
- Fix MCP server configuration to use same Settings system as main server ([1a4262d](../../commit/1a4262d))
- Merge pull request #6 from snapby/feature/mcp-server-integration ([d6d4cd8](../../commit/d6d4cd8))
- Merge pull request #7 from snapby/feature/mcp-chat-functionality ([c8c9f06](../../commit/c8c9f06))
- Merge pull request #8 from snapby/feature/mcp-streaming-server ([858ef5a](../../commit/858ef5a))
- Merge pull request #9 from snapby/feature/mcp-streaming-server ([857372a](../../commit/857372a))
- Merge pull request #10 from snapby/feature/migrate-to-fastmcp-2 ([f8b64ea](../../commit/f8b64ea))
- Merge pull request #11 from snapby/fix/csv-upload-tool-calling ([a53115b](../../commit/a53115b))
- Merge pull request #12 from snapby/fix/chat-database-initialization ([f417980](../../commit/f417980))
- Merge pull request #13 from snapby/fix/langgraph-llm-config ([d9e613a](../../commit/d9e613a))
- Merge pull request #14 from snapby/fix/anthropic-api-key-config ([7b6c21f](../../commit/7b6c21f))
- Merge pull request #15 from snapby/fix/env-file-loading ([c5c9185](../../commit/c5c9185))
- Merge pull request #16 from snapby/fix/chat-graph-messages-format ([1bce504](../../commit/1bce504))
- Merge pull request #17 from snapby/fix/add-debug-logging ([76ca34b](../../commit/76ca34b))
- Merge pull request #18 from snapby/fix/enhanced-message-logging ([a6084dc](../../commit/a6084dc))
- Fix tool result processing timeout - return structured data instead of JSON strings ([0d16a6a](../../commit/0d16a6a))
- Merge pull request #19 from snapby/fix/tool-result-processing-timeout ([5ad9c74](../../commit/5ad9c74))
- Fix datetime serialization in tool results ([086700d](../../commit/086700d))
- Merge pull request #20 from snapby/fix/tool-result-processing-timeout ([03099fb](../../commit/03099fb))
- Fix tool result content format for Anthropic API compatibility ([7a085e7](../../commit/7a085e7))
- Merge pull request #21 from snapby/fix/tool-result-processing-timeout ([3480999](../../commit/3480999))
- Add Docker MCP server configuration ([5084cc1](../../commit/5084cc1))
- Merge pull request #22 from snapby/fix/tool-result-processing-timeout ([d68ee02](../../commit/d68ee02))
- Fix Dockerfile.mcp build issues ([d81d4e4](../../commit/d81d4e4))
- Final Docker MCP server configuration fixes ([c8599e3](../../commit/c8599e3))
- Merge pull request #23 from snapby/fix/tool-result-processing-timeout ([0dbc461](../../commit/0dbc461))
- Fix Docker MCP server CMD execution issue ([fd9860a](../../commit/fd9860a))
- Merge pull request #24 from snapby/fix/tool-result-processing-timeout ([4d49a2e](../../commit/4d49a2e))
- Fix Docker health check 404 errors ([136eb70](../../commit/136eb70))
- Merge pull request #25 from snapby/fix/tool-result-processing-timeout ([4920309](../../commit/4920309))
- Remove Docker health check as requested ([ebac74d](../../commit/ebac74d))
- Merge pull request #26 from snapby/fix/tool-result-processing-timeout ([a415685](../../commit/a415685))
- Merge pull request #27 from snapby/fix/tool-result-processing-timeout ([5f6b50b](../../commit/5f6b50b))
- Merge pull request #28 from snapby/fix/tool-result-processing-timeout ([227cdad](../../commit/227cdad))
- Merge branch 'main' of https://github.com/snapby/snapture-sql-agent ([9de131e](../../commit/9de131e))
- Fix mypy error in src/app/graphs/chat/nodes/llm.py ([67132f6](../../commit/67132f6))
- Merge pull request #29 from snapby/fix-mypy-error-llm ([faa8b7b](../../commit/faa8b7b))

