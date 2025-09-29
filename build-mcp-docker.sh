#!/bin/bash
# Build script for MCP server Docker image

set -euo pipefail

# Configuration
IMAGE_NAME="snapture-sql-agent-mcp"
TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "🐳 Building MCP server Docker image: ${FULL_IMAGE_NAME}"

# Build the image
docker build -f Dockerfile.mcp -t "${FULL_IMAGE_NAME}" .

echo "✅ Successfully built Docker image: ${FULL_IMAGE_NAME}"

# Show image info
echo ""
echo "📊 Image information:"
docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}"

echo ""
echo "🚀 To run the MCP server:"
echo "docker run -p 3000:3000 --env-file .env ${FULL_IMAGE_NAME}"
echo ""
echo "🔍 To run with environment variables:"
echo "docker run -p 3000:3000 -e DATABASE_URL='your_db_url' -e ANTHROPIC_API_KEY='your_key' ${FULL_IMAGE_NAME}"
echo ""
echo "🛠️  To run in STDIO mode (for MCP client integration):"
echo "docker run -i --env-file .env ${FULL_IMAGE_NAME} fastmcp run mcp_server.py:mcp --transport stdio"
echo ""
echo "🧪 To test the container:"
echo "docker run --rm ${FULL_IMAGE_NAME} fastmcp --help"