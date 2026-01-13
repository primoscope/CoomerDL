# MCP Setup Guide for CoomerDL

This guide provides step-by-step instructions for setting up Model Context Protocol (MCP) servers to enhance AI agent capabilities when working with CoomerDL.

## What is MCP?

Model Context Protocol (MCP) is a standardized protocol that allows AI agents to access external tools, databases, APIs, and services. By configuring MCP servers, you enable AI agents (like GitHub Copilot) to:

- **Access databases** directly (SQLite, PostgreSQL)
- **Automate browsers** for testing (Puppeteer, Playwright)
- **Analyze code** with advanced tools (mypy, complexity metrics)
- **Search the web** for documentation and solutions
- **Maintain memory** across sessions
- **Execute complex reasoning** tasks

CoomerDL has been configured with **14+ MCP servers** covering all aspects of development, from database optimization to web scraping testing.

## Quick Start (Recommended)

### One-Line Installation

Choose your platform:

#### Unix/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/primoscope/CoomerDL/main/scripts/mcp/setup.sh | bash
```

#### Windows PowerShell
```powershell
iwr https://raw.githubusercontent.com/primoscope/CoomerDL/main/scripts/mcp/setup.ps1 -useb | iex
```

### Alternative: Local Installation

If you have the repository cloned locally:

```bash
# Unix/macOS
cd CoomerDL
./scripts/mcp/setup.sh

# Windows
cd CoomerDL
.\scripts\mcp\setup.ps1
```

## Prerequisites

Before installing MCP servers, ensure you have:

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **npm** (comes with Node.js)
   - Verify: `npm --version`

3. **Python 3.8+**
   - Download from: https://python.org/
   - Verify: `python --version` or `python3 --version`

4. **pip** (comes with Python)
   - Verify: `pip --version` or `python -m pip --version`

## Manual Installation

If you prefer to install servers manually or need to troubleshoot:

### Step 1: Install npm-based MCP Servers

```bash
# Core infrastructure
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @github/mcp-server

# Development tooling
npm install -g @anthropic/server-puppeteer
npm install -g @modelcontextprotocol/server-fetch

# Advanced features
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g mcp-server-docker
npm install -g mcp-server-yt-dlp

# Community servers
npm install -g @anthropic/server-playwright
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-brave-search
npm install -g mcp-server-postgres
```

### Step 2: Install Python-based MCP Servers

```bash
pip install mcp-server-python-analysis
```

### Step 3: Verify Installation

```bash
# Unix/macOS
./scripts/mcp/verify-installation.sh

# Windows
.\scripts\mcp\verify-installation.ps1
```

## Configuration

### For GitHub Copilot (Web UI)

1. Navigate to your repository on GitHub.com
2. Click **Settings** (repository settings, not account)
3. In the left sidebar, click **Copilot**
4. Click **MCP Servers** tab
5. Click **Add Server** or edit existing configuration
6. Copy the entire contents of `.github/copilot/mcp.json` from the repository
7. Paste into the configuration editor
8. Click **Save**

The MCP servers will now be automatically available to GitHub Copilot for all agents working on the repository.

### For Local Development

MCP servers are automatically configured via `.mcp/config.json` in the repository root. This file is read by AI tools that support MCP when working locally.

**No additional configuration needed** for local development after running the setup script.

## Environment Variables

Some MCP servers require environment variables to function. The configuration method differs for GitHub Copilot vs local development:

### For GitHub Copilot (Repository Secrets)

GitHub Copilot requires secrets to be added via **Settings → Secrets and variables → Actions** with the `COPILOT_MCP_` prefix:

**Required:**
- `COPILOT_MCP_GITHUB_TOKEN` - GitHub personal access token for repository operations

**Optional:**
- `COPILOT_MCP_BRAVE_API_KEY` - Brave Search API key for web search
- `COPILOT_MCP_POSTGRES_CONNECTION_STRING` - PostgreSQL connection string (future use)

**Adding Repository Secrets:**

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `COPILOT_MCP_GITHUB_TOKEN`
   - Value: Your GitHub token (see below for creating one)
5. Click **Add secret**

### For Local Development (Shell Environment Variables)

For local MCP tools, use standard environment variable names without the prefix:

**Required:**
- `GITHUB_TOKEN` - GitHub personal access token
- `PROJECT_PATH` - Set automatically to current directory by configs

**Optional:**
- `BRAVE_API_KEY` - Brave Search API key
- `POSTGRES_CONNECTION_STRING` - PostgreSQL connection string

### Creating a GitHub Token

Required for the GitHub MCP server to access repository data, PRs, issues, and workflows.

**Steps:**

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Give it a descriptive name (e.g., "CoomerDL MCP Server")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click **Generate token**
6. Copy the token (you won't see it again!)

**Setting for Local Development:**

Unix/macOS (Bash/Zsh):
```bash
export GITHUB_TOKEN="ghp_your_token_here"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
```

Windows (PowerShell):
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"

# For persistence, add to PowerShell profile
Add-Content $PROFILE "`n`$env:GITHUB_TOKEN = 'ghp_your_token_here'"
```

Windows (System Environment Variables):
1. Right-click **This PC** → **Properties**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, click **New**
5. Variable name: `GITHUB_TOKEN`
6. Variable value: `ghp_your_token_here`
7. Click **OK**

**Setting for GitHub Copilot:**

Add the token as a repository secret named `COPILOT_MCP_GITHUB_TOKEN` (see "Adding Repository Secrets" above).

### Optional: Brave Search API Key

Enables web search for finding documentation and troubleshooting.

**Getting a Brave API Key:**

1. Go to https://brave.com/search/api/
2. Sign up for a free account
3. Create an API key
4. Copy the key

**Setting for Local Development:**
```bash
export BRAVE_API_KEY="your_brave_key_here"
```

**Setting for GitHub Copilot:**

Add as repository secret named `COPILOT_MCP_BRAVE_API_KEY`.

### Optional: PostgreSQL Connection String

For future PostgreSQL migration (currently optional).

**Format:**
```bash
export POSTGRES_CONNECTION_STRING="postgresql://user:password@host:port/database"
```

**Setting for GitHub Copilot:**

Add as repository secret named `COPILOT_MCP_POSTGRES_CONNECTION_STRING`.

## Verification

After installation, verify everything is working:

```bash
# Unix/macOS
./scripts/mcp/verify-installation.sh

# Windows (if verification script exists)
.\scripts\mcp\verify-installation.ps1
```

The verification script will check:
- ✅ Prerequisites (Node.js, npm, Python)
- ✅ Configuration files
- ✅ JSON validity
- ✅ Environment variables
- ✅ Server accessibility

## Testing MCP Servers

### Test with an AI Agent

If you have GitHub Copilot or another MCP-compatible AI tool:

**Test Prompt 1: Filesystem Server**
```
"List all Python files in the downloader/ directory"
```

**Test Prompt 2: SQLite Server**
```
"Show me the schema of the downloads.db database"
```

**Test Prompt 3: GitHub Server**
```
"Find all occurrences of 'threading.Event' in the repository"
```

**Test Prompt 4: Python Analysis**
```
"Run mypy type checking on downloader/base.py"
```

### Manual Server Test

Test individual servers manually:

```bash
# Test filesystem server
npx -y @modelcontextprotocol/server-filesystem /path/to/CoomerDL

# Test SQLite server
npx -y @modelcontextprotocol/server-sqlite --db-path resources/config/downloads.db

# Test GitHub server (requires GITHUB_TOKEN)
npx -y @github/mcp-server

# Test fetch server
npx -y @modelcontextprotocol/server-fetch
```

## Troubleshooting

### Issue: "npx: command not found"

**Cause**: npm is not installed or not in PATH

**Solution**:
1. Install Node.js from https://nodejs.org/
2. Restart your terminal
3. Verify: `npm --version`

### Issue: "Module not found" for Python servers

**Cause**: Python module not installed or wrong Python version

**Solution**:
```bash
# Verify Python version (need 3.8+)
python --version

# Reinstall Python MCP server
pip install --upgrade mcp-server-python-analysis

# Test module
python -m mcp_server_python_analysis --help
```

### Issue: GitHub server returns 401 Unauthorized

**Cause**: GITHUB_TOKEN not set or invalid

**Solution**:
1. Verify token is set: `echo $GITHUB_TOKEN`
2. Check token hasn't expired on GitHub
3. Verify token has correct scopes (`repo`, `read:org`, `workflow`)
4. Generate a new token if needed

### Issue: SQLite server can't find database

**Cause**: Database path is incorrect or database doesn't exist

**Solution**:
1. Verify database exists: `ls -la resources/config/downloads.db`
2. Use absolute path in configuration
3. Run CoomerDL once to create the database if missing

### Issue: Permission denied on scripts

**Cause**: Scripts don't have execute permissions

**Solution**:
```bash
chmod +x scripts/mcp/*.sh
```

### Issue: Servers work but agents can't access them

**Cause**: Configuration not loaded or MCP not enabled in AI tool

**Solution**:
1. Verify `.github/copilot/mcp.json` exists
2. Check GitHub repository settings (Settings → Copilot → MCP Servers)
3. Restart your AI tool
4. Check AI tool supports MCP (GitHub Copilot, Claude Desktop, etc.)

## Using MCP Servers with Agents

Once configured, agents can automatically use MCP servers. You don't need to explicitly mention them in most cases.

### Example Use Cases

#### Database Optimization
```
Prompt: "Analyze the downloads.db database and suggest performance improvements"

Agent will:
1. Use SQLite server to inspect schema
2. Run EXPLAIN on queries
3. Suggest indexes
4. Provide migration SQL
```

#### Web Scraper Testing
```
Prompt: "Test the Coomer scraper with URL https://example.com/post/123"

Agent will:
1. Use Puppeteer to load the page
2. Use Fetch to get HTML
3. Compare with scraper output
4. Report any discrepancies
```

#### Type Checking
```
Prompt: "Run mypy on all Python files and fix type errors"

Agent will:
1. Use Python Analysis server for mypy
2. Identify type errors
3. Use Filesystem server to read/write files
4. Fix annotations
5. Verify fixes
```

#### Code Search
```
Prompt: "Find all places where we handle download cancellation"

Agent will:
1. Use GitHub server to search code
2. Analyze patterns
3. Suggest improvements
```

## Advanced Configuration

### Custom Server Paths

To customize server paths or add new servers, edit:

- **`.github/copilot/mcp.json`** - For GitHub Copilot
- **`.mcp/config.json`** - For local development

Example: Using a local yt-dlp binary instead of npm package:

```json
{
  "yt-dlp": {
    "command": "/usr/local/bin/yt-dlp",
    "args": ["--version"]
  }
}
```

### Server-Specific Options

Each server may support additional options. Check the individual server documentation:

- Filesystem: Can restrict to specific directories
- SQLite: Can set read-only mode
- GitHub: Can limit to specific repositories
- Python Analysis: Can customize mypy configuration

See `.github/mcp/servers/*.json` for server-specific configurations.

## Uninstalling

To remove MCP servers:

### npm servers
```bash
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @modelcontextprotocol/server-sqlite
# ... repeat for all npm servers
```

### Python servers
```bash
pip uninstall mcp-server-python-analysis
```

### Configuration files
```bash
# Remove configuration (optional)
rm -rf .mcp/
rm -rf .github/copilot/mcp.json
```

## Additional Resources

- **Full Documentation**: `.github/mcp/README.md`
- **MCP Specification**: https://github.com/modelcontextprotocol/specification
- **MCP Servers Registry**: https://github.com/modelcontextprotocol/servers
- **GitHub MCP Server**: https://github.com/github/mcp-server
- **CoomerDL Repository**: https://github.com/primoscope/CoomerDL

## Getting Help

If you encounter issues:

1. Run the verification script: `./scripts/mcp/verify-installation.sh`
2. Check the troubleshooting section above
3. Review server logs (if available)
4. Open an issue: https://github.com/primoscope/CoomerDL/issues

## Contributing

To add or update MCP servers:

1. Add server configuration to `.github/mcp/servers/`
2. Update `.github/copilot/mcp.json` and `.mcp/config.json`
3. Add installation steps to setup scripts
4. Update documentation
5. Submit a pull request

---

**Version**: 1.0  
**Last Updated**: 2026-01-13  
**Maintained by**: CoomerDL Project
