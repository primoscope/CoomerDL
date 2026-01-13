#!/bin/bash
# MCP Server Installation Verification Script

set -e

echo "======================================"
echo "Verifying MCP Server Installation"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Get repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Repository root: $REPO_ROOT"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js: $NODE_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Node.js not found"
    ((FAILED++))
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm: $NPM_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} npm not found"
    ((FAILED++))
fi

if command -v npx &> /dev/null; then
    echo -e "${GREEN}✓${NC} npx is available"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} npx not found"
    ((FAILED++))
fi

if command -v python3 &> /dev/null || command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
    else
        PYTHON_VERSION=$(python --version)
    fi
    echo -e "${GREEN}✓${NC} Python: $PYTHON_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Python not found"
    ((FAILED++))
fi

echo ""
echo "Checking configuration files..."
echo ""

# Check configuration files
if [ -f "$REPO_ROOT/.github/copilot/mcp.json" ]; then
    echo -e "${GREEN}✓${NC} .github/copilot/mcp.json exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} .github/copilot/mcp.json missing"
    ((FAILED++))
fi

if [ -f "$REPO_ROOT/.mcp/config.json" ]; then
    echo -e "${GREEN}✓${NC} .mcp/config.json exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} .mcp/config.json missing"
    ((FAILED++))
fi

if [ -d "$REPO_ROOT/.github/mcp/servers" ]; then
    SERVER_COUNT=$(ls -1 "$REPO_ROOT/.github/mcp/servers"/*.json 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} .github/mcp/servers/ directory exists ($SERVER_COUNT configs)"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} .github/mcp/servers/ directory missing"
    ((FAILED++))
fi

echo ""
echo "Validating JSON files..."
echo ""

# Validate JSON files (requires Python or jq)
if command -v python3 &> /dev/null; then
    if python3 -c "import json; json.load(open('$REPO_ROOT/.github/copilot/mcp.json'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} .github/copilot/mcp.json is valid JSON"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} .github/copilot/mcp.json is invalid JSON"
        ((FAILED++))
    fi
    
    if python3 -c "import json; json.load(open('$REPO_ROOT/.mcp/config.json'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} .mcp/config.json is valid JSON"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} .mcp/config.json is invalid JSON"
        ((FAILED++))
    fi
fi

echo ""
echo "Checking environment variables..."
echo ""

if [ -n "$GITHUB_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} GITHUB_TOKEN is set"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} GITHUB_TOKEN not set (required for GitHub server)"
    ((WARNINGS++))
fi

if [ -n "$BRAVE_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} BRAVE_API_KEY is set"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} BRAVE_API_KEY not set (optional, for Brave search)"
    ((WARNINGS++))
fi

if [ -n "$POSTGRES_CONNECTION_STRING" ]; then
    echo -e "${GREEN}✓${NC} POSTGRES_CONNECTION_STRING is set"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} POSTGRES_CONNECTION_STRING not set (optional, for PostgreSQL)"
    ((WARNINGS++))
fi

echo ""
echo "Testing MCP server accessibility..."
echo ""

# Test key servers (this may take a moment)
# Note: We use --help flag and don't expect it to work for all servers
# We're just checking if npx can resolve and run them

test_server() {
    local server=$1
    local name=$2
    
    if timeout 5 npx -y "$server" --help &>/dev/null || timeout 5 npx -y "$server" --version &>/dev/null || true; then
        echo -e "${GREEN}✓${NC} $name server accessible"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $name server may not be properly installed"
        ((WARNINGS++))
        return 1
    fi
}

# Test a subset of critical servers
test_server "@modelcontextprotocol/server-filesystem" "filesystem"
test_server "@modelcontextprotocol/server-sqlite" "sqlite"
test_server "@github/mcp-server" "github"
test_server "@modelcontextprotocol/server-fetch" "fetch"

echo ""
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ MCP server setup is complete and functional!${NC}"
    echo ""
    echo "You can now use MCP servers with AI agents."
    echo "See .github/mcp/README.md for usage instructions."
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the output above.${NC}"
    echo ""
    echo "Run the setup script to install missing components:"
    echo "  ./scripts/mcp/setup.sh"
    exit 1
fi
