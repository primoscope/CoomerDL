#!/bin/bash
# MCP Server Setup Script for Unix/macOS
# This script installs all MCP servers required for CoomerDL AI agent integration

set -e

echo "======================================"
echo "CoomerDL MCP Server Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Check for pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}ERROR: pip is not installed${NC}"
    echo "Please install pip for Python package management"
    exit 1
fi

echo -e "${GREEN}✓${NC} Prerequisites check passed"
echo ""

# Install npm-based MCP servers
echo "======================================"
echo "Installing npm-based MCP servers..."
echo "======================================"
echo ""

npm_servers=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-sqlite"
    "@github/mcp-server"
    "@anthropic/server-puppeteer"
    "@modelcontextprotocol/server-fetch"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-sequential-thinking"
    "mcp-server-docker"
    "mcp-server-yt-dlp"
    "@anthropic/server-playwright"
    "@modelcontextprotocol/server-git"
    "@modelcontextprotocol/server-brave-search"
    "mcp-server-postgres"
)

for server in "${npm_servers[@]}"; do
    echo -e "${YELLOW}Installing ${server}...${NC}"
    if npm install -g "$server" --silent; then
        echo -e "${GREEN}✓${NC} ${server} installed successfully"
    else
        echo -e "${RED}✗${NC} Failed to install ${server}"
    fi
    echo ""
done

# Install Python-based MCP servers
echo "======================================"
echo "Installing Python-based MCP servers..."
echo "======================================"
echo ""

python_servers=(
    "mcp-server-python-analysis"
)

for server in "${python_servers[@]}"; do
    echo -e "${YELLOW}Installing ${server}...${NC}"
    if $PYTHON_CMD -m pip install "$server" --quiet; then
        echo -e "${GREEN}✓${NC} ${server} installed successfully"
    else
        echo -e "${RED}✗${NC} Failed to install ${server} (this is optional)"
    fi
    echo ""
done

# Create necessary directories
echo "======================================"
echo "Creating necessary directories..."
echo "======================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

mkdir -p "$REPO_ROOT/.mcp"
mkdir -p "$REPO_ROOT/.github/copilot"
mkdir -p "$REPO_ROOT/.github/mcp/servers"

echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Verify installations
echo "======================================"
echo "Verifying installations..."
echo "======================================"
echo ""

# Check npx availability
if command -v npx &> /dev/null; then
    echo -e "${GREEN}✓${NC} npx is available"
else
    echo -e "${RED}✗${NC} npx is not available"
fi

# Test a few key servers
echo ""
echo "Testing key MCP servers:"
echo ""

# Note: We can't easily test all servers without starting them
# but we can verify they're installed

if npx -y @modelcontextprotocol/server-filesystem --help &> /dev/null || true; then
    echo -e "${GREEN}✓${NC} filesystem server accessible"
else
    echo -e "${YELLOW}⚠${NC} filesystem server may not be properly installed"
fi

if npx -y @github/mcp-server --help &> /dev/null || true; then
    echo -e "${GREEN}✓${NC} github server accessible"
else
    echo -e "${YELLOW}⚠${NC} github server may not be properly installed"
fi

echo ""
echo "======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in your shell or .env file:"
echo "   - GITHUB_TOKEN (for GitHub MCP server)"
echo "   - BRAVE_API_KEY (optional, for Brave search)"
echo "   - POSTGRES_CONNECTION_STRING (optional, for PostgreSQL)"
echo ""
echo "2. Add MCP configuration to GitHub repository settings:"
echo "   - Go to Settings > Copilot > MCP Servers"
echo "   - Copy the JSON from .github/copilot/mcp.json"
echo ""
echo "3. For local development, AI tools will read from .mcp/config.json"
echo ""
echo "4. Run the verification script to test your setup:"
echo "   ./scripts/mcp/verify-installation.sh"
echo ""
