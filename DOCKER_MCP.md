# 🐳 Docker MCP Server

This document explains how to build and run the Snapture SQL Agent MCP server using Docker.

## 📦 Dockerfile.mcp Overview

The `Dockerfile.mcp` creates a containerized version of the MCP server with the following features:

- **Multi-stage build** for optimized image size
- **Python 3.13** runtime with UV package manager
- **Non-root user** for enhanced security
- **Health checks** for container monitoring
- **Port 3000** exposed for HTTP transport
- **FastMCP 2.0** for MCP server functionality

### Build Architecture

```dockerfile
Stage 1 (builder): ghcr.io/astral-sh/uv:python3.13-bookworm-slim
├── Install dependencies with UV
├── Copy source code
└── Build application

Stage 2 (runtime): python:3.13-slim-bookworm
├── Create non-root user (app:app)
├── Copy built application from builder
├── Set environment variables
└── Configure MCP server
```

## 🚀 Quick Start

### 1. Build the Docker Image

```bash
# Using the build script (recommended)
./build-mcp-docker.sh

# Or manually
docker build -f Dockerfile.mcp -t snapture-sql-agent-mcp:latest .
```

### 2. Run the MCP Server

#### HTTP Mode (Default)
```bash
# With environment file
docker run -p 3000:3000 --env-file .env snapture-sql-agent-mcp:latest

# With individual environment variables
docker run -p 3000:3000 \
  -e DATABASE_URL="your_database_url" \
  -e ANTHROPIC_API_KEY="your_api_key" \
  snapture-sql-agent-mcp:latest
```

#### STDIO Mode (for MCP Client Integration)
```bash
docker run -i --env-file .env snapture-sql-agent-mcp:latest \
  fastmcp run mcp_server.py:mcp --transport stdio
```

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | DuckDB database connection URL | `duckdb:///data/mydb.duckdb` |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | `sk-ant-...` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_DEBUG` | Enable debug logging | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🔧 Advanced Usage

### Custom Port
```bash
docker run -p 8080:8080 --env-file .env snapture-sql-agent-mcp:latest \
  fastmcp run mcp_server.py:mcp --transport http --port 8080 --host 0.0.0.0
```

### Volume Mounting for Database
```bash
# Mount local database directory
docker run -p 3000:3000 --env-file .env \
  -v /path/to/local/db:/app/data \
  snapture-sql-agent-mcp:latest
```

### Debug Mode
```bash
docker run -p 3000:3000 --env-file .env \
  -e MCP_DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  snapture-sql-agent-mcp:latest
```

## 🏥 Health Checks

The container includes a health check that verifies the MCP server is responding:

```bash
# Check container health
docker ps  # Look for "healthy" status

# Manual health check
docker exec <container_id> pgrep -f \"fastmcp run\"
```

## 🔍 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs <container_id>

# Run interactively for debugging
docker run -it --env-file .env snapture-sql-agent-mcp:latest bash
```

### Port Already in Use
```bash
# Use a different port
docker run -p 3001:3000 --env-file .env snapture-sql-agent-mcp:latest
```

### Database Connection Issues
```bash
# Verify environment variables
docker run --env-file .env snapture-sql-agent-mcp:latest env | grep DATABASE_URL

# Test database connectivity
docker run -it --env-file .env snapture-sql-agent-mcp:latest \
  python -c "import duckdb; print('DuckDB OK')"
```

## 📝 Development

### Building Different Versions
```bash
# Build with specific tag
./build-mcp-docker.sh v1.0.0

# Build development version
docker build -f Dockerfile.mcp -t snapture-sql-agent-mcp:dev .
```

### Testing the Container
```bash
# Run tests inside container
docker run --env-file .env snapture-sql-agent-mcp:latest \
  uv run pytest

# Interactive development
docker run -it -v $(pwd):/app --env-file .env \
  snapture-sql-agent-mcp:latest bash
```

## 🚢 Deployment

### Docker Compose (Recommended)

Create a `docker-compose.mcp.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "3000:3000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "pgrep", "-f", "fastmcp run"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      - ./data:/app/data  # Optional: for persistent database storage
```

Run with:
```bash
docker-compose -f docker-compose.mcp.yml up -d
```

### Production Considerations

1. **Security**: Use secrets management for API keys
2. **Monitoring**: Integrate with your monitoring stack
3. **Logging**: Configure log aggregation
4. **Backup**: Ensure database data is backed up
5. **Updates**: Set up automated image updates

## 📊 Container Specifications

| Aspect | Details |
|--------|---------|
| Base Image | `python:3.13-slim-bookworm` |
| Package Manager | UV (ultra-fast Python package manager) |
| User | Non-root (`app:app`, UID/GID 1000) |
| Working Directory | `/app` |
| Default Port | `3000` |
| Health Check | Process check (`pgrep fastmcp`) |
| Entry Point | `uv run` |
| Default Command | FastMCP server on HTTP transport |

This Docker setup provides a robust, secure, and efficient way to deploy the Snapture SQL Agent MCP server in any containerized environment.