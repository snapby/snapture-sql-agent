# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [[36m0.1.0[39m] - 2025-09-30

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
- Fix tool result processing timeout - return structured data instead of JSON strings ([0d16a6a](../../commit/0d16a6a))
- Fix datetime serialization in tool results ([086700d](../../commit/086700d))
- Fix tool result content format for Anthropic API compatibility ([7a085e7](../../commit/7a085e7))
- Add Docker MCP server configuration ([5084cc1](../../commit/5084cc1))
- Fix Dockerfile.mcp build issues ([d81d4e4](../../commit/d81d4e4))
- Final Docker MCP server configuration fixes ([c8599e3](../../commit/c8599e3))
- Fix Docker MCP server CMD execution issue ([fd9860a](../../commit/fd9860a))
- Fix Docker health check 404 errors ([136eb70](../../commit/136eb70))
- Remove Docker health check as requested ([ebac74d](../../commit/ebac74d))

