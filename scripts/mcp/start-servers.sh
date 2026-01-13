#!/bin/bash
# MCP Server Start Script
# This script can be used to manually start MCP servers if needed

set -e

echo "======================================"
echo "Starting MCP Servers for CoomerDL"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Repository root: $REPO_ROOT"
echo ""

# Check for required environment variables
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}WARNING: GITHUB_TOKEN not set. GitHub MCP server may not work.${NC}"
fi

if [ -z "$BRAVE_API_KEY" ]; then
    echo -e "${YELLOW}WARNING: BRAVE_API_KEY not set. Brave search will not work.${NC}"
fi

echo ""
echo "MCP servers are designed to be started automatically by AI agents."
echo "They use 'npx -y' to run on-demand without persistent processes."
echo ""
echo "If you need to test a specific server, you can run:"
echo ""
echo "  npx -y @modelcontextprotocol/server-filesystem $REPO_ROOT"
echo "  npx -y @modelcontextprotocol/server-sqlite --db-path resources/config/downloads.db"
echo "  npx -y @github/mcp-server"
echo ""
echo "For more information, see:"
echo "  - .github/mcp/README.md"
echo "  - MCP_SETUP_GUIDE.md"
echo ""
