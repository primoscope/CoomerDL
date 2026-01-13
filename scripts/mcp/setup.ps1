# MCP Server Setup Script for Windows PowerShell
# This script installs all MCP servers required for CoomerDL AI agent integration

$ErrorActionPreference = "Continue"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "CoomerDL MCP Server Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check for Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js is installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check for npm
try {
    $npmVersion = npm --version
    Write-Host "✓ npm is installed: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: npm is not installed" -ForegroundColor Red
    Write-Host "Please install npm (usually comes with Node.js)" -ForegroundColor Yellow
    exit 1
}

# Check for Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = & $pythonCmd --version
Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green

# Check for pip
try {
    & $pythonCmd -m pip --version | Out-Null
    Write-Host "✓ pip is installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pip is not installed" -ForegroundColor Red
    Write-Host "Please install pip for Python package management" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Installing npm-based MCP servers..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$npmServers = @(
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-sqlite",
    "@github/mcp-server",
    "@anthropic/server-puppeteer",
    "@modelcontextprotocol/server-fetch",
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-sequential-thinking",
    "mcp-server-docker",
    "mcp-server-yt-dlp",
    "@anthropic/server-playwright",
    "@modelcontextprotocol/server-git",
    "@modelcontextprotocol/server-brave-search",
    "mcp-server-postgres"
)

foreach ($server in $npmServers) {
    Write-Host "Installing $server..." -ForegroundColor Yellow
    try {
        npm install -g $server --silent 2>&1 | Out-Null
        Write-Host "✓ $server installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install $server" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Installing Python-based MCP servers..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$pythonServers = @(
    "mcp-server-python-analysis"
)

foreach ($server in $pythonServers) {
    Write-Host "Installing $server..." -ForegroundColor Yellow
    try {
        & $pythonCmd -m pip install $server --quiet 2>&1 | Out-Null
        Write-Host "✓ $server installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install $server (this is optional)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Creating necessary directories..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

New-Item -ItemType Directory -Force -Path "$repoRoot\.mcp" | Out-Null
New-Item -ItemType Directory -Force -Path "$repoRoot\.github\copilot" | Out-Null
New-Item -ItemType Directory -Force -Path "$repoRoot\.github\mcp\servers" | Out-Null

Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Verifying installations..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check npx availability
try {
    npx --version | Out-Null
    Write-Host "✓ npx is available" -ForegroundColor Green
} catch {
    Write-Host "✗ npx is not available" -ForegroundColor Red
}

Write-Host ""
Write-Host "Testing key MCP servers:" -ForegroundColor Yellow
Write-Host ""

# Test filesystem server
try {
    npx -y @modelcontextprotocol/server-filesystem --help 2>&1 | Out-Null
    Write-Host "✓ filesystem server accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠ filesystem server may not be properly installed" -ForegroundColor Yellow
}

# Test GitHub server
try {
    npx -y @github/mcp-server --help 2>&1 | Out-Null
    Write-Host "✓ github server accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠ github server may not be properly installed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Configure environment variables:"
Write-Host "   - GITHUB_TOKEN (for GitHub MCP server)"
Write-Host "   - BRAVE_API_KEY (optional, for Brave search)"
Write-Host "   - POSTGRES_CONNECTION_STRING (optional, for PostgreSQL)"
Write-Host ""
Write-Host "2. Add MCP configuration to GitHub repository settings:"
Write-Host "   - Go to Settings > Copilot > MCP Servers"
Write-Host "   - Copy the JSON from .github/copilot/mcp.json"
Write-Host ""
Write-Host "3. For local development, AI tools will read from .mcp/config.json"
Write-Host ""
Write-Host "4. Run the verification script to test your setup:"
Write-Host "   .\scripts\mcp\verify-installation.ps1"
Write-Host ""
