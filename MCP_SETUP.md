# MCP Server Setup Guide

## Prerequisites

### 1. Anthropic API Key (Required)

The MCP server requires an Anthropic API key to enable chat functionality with your data.

1. **Get an API Key**:
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Sign up or log in
   - Create a new API key

2. **Configure Environment Variable**:
   
   **Option A: Using .env file (Recommended)**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit the .env file and add your API key
   nano .env
   ```
   
   Add your key to `.env`:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```
   
   **Option B: Export directly**
   ```bash
   export ANTHROPIC_API_KEY="your_actual_api_key_here"
   ```

### 2. Verify Configuration

Test that your API key is properly configured:

```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY

# Or test the MCP server directly
uv run python mcp_server.py --http --port 8080
```

## Running the MCP Server

### HTTP Mode (Recommended)
```bash
# Using Makefile
make mcp-http

# Or directly
uv run python mcp_server.py --http --port 8080
```

### STDIO Mode
```bash
# Using Makefile  
make mcp-stdio

# Or directly
uv run python mcp_server.py
```

## Testing with MCP Inspector

1. **Install MCP Inspector**:
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Test HTTP Mode**:
   ```bash
   mcp-inspector http://localhost:8080/mcp
   ```

3. **Test Workflow**:
   - Upload CSV data: Use `upload_csv_from_url` tool
   - Query database: Use `execute_sql_query` tool  
   - Chat with data: Use `chat_with_data` tool
   - Stream analysis: Use `chat_with_data_stream` tool

## Common Issues

### Authentication Error
```
"Could not resolve authentication method. Expected either api_key or auth_token to be set"
```

**Solution**: Ensure `ANTHROPIC_API_KEY` is set in your environment:
```bash
# Check if set
echo $ANTHROPIC_API_KEY

# If empty, set it:
export ANTHROPIC_API_KEY="your_key_here"
```

### Chat Tools Not Working
If chat functionality fails, verify:

1. ✅ API key is configured
2. ✅ Server is running in HTTP mode
3. ✅ Database has uploaded CSV data
4. ✅ All dependencies are installed

### Environment Variables Not Loading

If using `.env` file but variables aren't loading:

```bash
# Load manually for testing
source .env
echo $ANTHROPIC_API_KEY
```

## Available Tools

| Tool | Description | Requires API Key |
|------|-------------|------------------|
| `execute_sql_query` | Execute SQL against uploaded data | ❌ No |
| `upload_csv_data` | Upload CSV string to database | ❌ No |
| `upload_csv_from_url` | Fetch and upload CSV from URL | ❌ No |  
| `get_database_schema` | Show database structure | ❌ No |
| `chat_with_data` | Natural language data analysis | ✅ **Yes** |
| `chat_with_data_stream` | Streaming data analysis | ✅ **Yes** |

## Example Workflow

```json
// 1. Upload CSV data
{
  "tool": "upload_csv_from_url",
  "arguments": {
    "url": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
    "table_name": "titanic",
    "description": "Titanic passenger data"
  }
}

// 2. Chat with data (requires API key)
{
  "tool": "chat_with_data",
  "arguments": {
    "question": "What was the survival rate by passenger class?"
  }
}
```

## Troubleshooting

1. **Check logs**: Server logs will show authentication errors
2. **Verify API key**: Test with a simple API call
3. **Check network**: Ensure no firewall blocks port 8080
4. **Dependencies**: Run `uv sync` to ensure all packages are installed