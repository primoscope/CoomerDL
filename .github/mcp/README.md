# MCP Server Configuration for CoomerDL

This directory contains comprehensive MCP (Model Context Protocol) server configurations for enhancing AI agent capabilities when working on CoomerDL. All 14+ MCP servers are fully configured and ready to use.

**Important:** The configuration includes GitHub Copilot-specific schema requirements:
- Each server has `"type": "stdio"` field
- Each server has a `"tools"` array listing available tools
- Environment variables use `COPILOT_MCP_` prefix for repository secrets
- Paths use relative references (`.`) for portability

## What is MCP?

MCP is a protocol that allows AI agents to access external tools, data sources, and services through standardized server interfaces. This enables agents to:

- Access specialized tools beyond basic file operations
- Query external data sources
- Integrate with development tools and APIs
- Maintain context across sessions
- Perform complex operations like browser automation and code analysis

## Quick Start

### One-Line Installation (Unix/macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/primoscope/CoomerDL/main/scripts/mcp/setup.sh | bash
```

### Manual Installation

```bash
# Clone and navigate to repository
cd CoomerDL

# Run setup script
./scripts/mcp/setup.sh        # Unix/macOS
# OR
.\scripts\mcp\setup.ps1        # Windows PowerShell

# Verify installation
./scripts/mcp/verify-installation.sh
```

## Configured MCP Servers

### Priority 1: Core Infrastructure

#### 1. **Filesystem Server** (`@modelcontextprotocol/server-filesystem`)

**Purpose**: Primary file system operations for the CoomerDL repository

**Capabilities**:
- Read/write files
- List directories
- Create/move/delete files
- Search for files

**Use Cases**:
- Reading source code
- Modifying configuration files
- Creating new components
- Organizing project structure

**Configuration**:
```json
{
  "filesystem": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    "tools": ["read_file", "read_multiple_files", "write_file", "edit_file", "create_directory", "list_directory", "move_file", "search_files", "get_file_info", "list_allowed_directories"]
  }
}
```

#### 2. **SQLite Server** (`@modelcontextprotocol/server-sqlite`)

**Purpose**: Direct database inspection and optimization for downloads.db

**Capabilities**:
- Execute SQL queries
- Analyze query plans (EXPLAIN)
- List tables and schemas
- Performance statistics
- Index recommendations

**Use Cases**:
- Debugging download tracking issues
- Optimizing database queries
- Analyzing job history
- Creating database migrations

**Configuration**:
```json
{
  "sqlite": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "resources/config/downloads.db"],
    "tools": ["read_query", "write_query", "create_table", "list_tables", "describe_table", "append_insight"]
  }
}
```

#### 3. **GitHub Server** (`@github/mcp-server`)

**Purpose**: Enhanced GitHub repository interaction

**Capabilities**:
- Search code across repository
- Access PR reviews and comments
- Query GitHub Actions results
- Search issues and discussions
- Create/update issues and PRs

**Use Cases**:
- Finding code patterns
- Reviewing PR feedback
- Tracking CI/CD results
- Managing issues

**Configuration**:
```json
{
  "github": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@github/mcp-server"],
    "env": {
      "GITHUB_TOKEN": "${COPILOT_MCP_GITHUB_TOKEN}"
    },
    "tools": ["get_file_contents", "get_issue", "get_pull_request", "list_issues", "list_pull_requests", "search_code", "search_issues", "search_repositories", "create_issue", "create_pull_request", "update_issue", "create_or_update_file", "push_files", "create_branch", "list_commits", "list_branches"]
  }
}
```

**Required**: Set `COPILOT_MCP_GITHUB_TOKEN` repository secret (for GitHub Copilot) or `GITHUB_TOKEN` environment variable (for local development)

### Priority 2: Development Tooling

#### 4. **Python Analysis Server** (`mcp-server-python-analysis`)

**Purpose**: Advanced Python static analysis and code quality

**Capabilities**:
- Static type checking (mypy)
- Cyclomatic complexity analysis
- Cognitive complexity metrics
- Import graph analysis
- Dependency vulnerability scanning

**Use Cases**:
- Type checking before commits
- Identifying complex functions
- Refactoring guidance
- Security audits

**Configuration**:
```json
{
  "python-analysis": {
    "command": "python",
    "args": ["-m", "mcp_server_python_analysis"],
    "env": {
      "PROJECT_PATH": "/path/to/CoomerDL"
    }
  }
}
```

**Installation**:
```bash
pip install mcp-server-python-analysis
```

#### 5. **Puppeteer Server** (`@anthropic/server-puppeteer`)

**Purpose**: Browser automation for testing scrapers

**Capabilities**:
- Navigate to URLs
- Click elements
- Fill forms
- Take screenshots
- Execute JavaScript
- Wait for dynamic content

**Use Cases**:
- Testing web scrapers
- Debugging JavaScript-heavy sites
- Validating browser cookie extraction
- Testing authentication flows

**Configuration**:
```json
{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@anthropic/server-puppeteer"]
  }
}
```

#### 6. **Fetch Server** (`@modelcontextprotocol/server-fetch`)

**Purpose**: HTTP/web content retrieval

**Capabilities**:
- Fetch URLs
- Parse HTML
- Extract JSON
- Handle redirects

**Use Cases**:
- Testing API endpoints
- Debugging HTTP responses
- Validating URL patterns
- Inspecting web content

**Configuration**:
```json
{
  "fetch": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-fetch"]
  }
}
```

### Priority 3: Advanced Features

#### 7. **Memory Server** (`@modelcontextprotocol/server-memory`)

**Purpose**: Persistent agent memory across sessions

**Capabilities**:
- Store entities and facts
- Create relationships
- Query knowledge graph
- Maintain context

**Use Cases**:
- Remember architectural decisions
- Track learned patterns
- Maintain project context
- Store debugging insights

**Configuration**:
```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

#### 8. **Sequential Thinking Server** (`@modelcontextprotocol/server-sequential-thinking`)

**Purpose**: Complex reasoning and multi-step problem solving

**Capabilities**:
- Step-by-step analysis
- Problem decomposition
- Logical reasoning

**Use Cases**:
- Architectural decisions
- Debugging complex issues
- Algorithm optimization
- Design patterns

**Configuration**:
```json
{
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
  }
}
```

#### 9. **Docker Server** (`mcp-server-docker`)

**Purpose**: Container operations for testing and deployment

**Capabilities**:
- List/create containers
- Start/stop containers
- Execute commands
- Inspect containers

**Use Cases**:
- Testing in isolated environments
- Creating reproducible builds
- Container-based deployment
- CI/CD integration

**Configuration**:
```json
{
  "docker": {
    "command": "npx",
    "args": ["-y", "mcp-server-docker"]
  }
}
```

#### 10. **yt-dlp Server** (`mcp-server-yt-dlp`)

**Purpose**: Direct yt-dlp integration for testing

**Capabilities**:
- Extract video info
- List available formats
- Download videos
- Get subtitles

**Use Cases**:
- Testing ytdlp_adapter.py
- Validating format selection
- Debugging download issues
- Comparing implementations

**Configuration**:
```json
{
  "yt-dlp": {
    "command": "npx",
    "args": ["-y", "mcp-server-yt-dlp"]
  }
}
```

### Priority 4: Community Servers

#### 11. **Playwright Server** (`@anthropic/server-playwright`)

**Purpose**: Multi-browser automation

**Capabilities**:
- Chrome, Firefox, Safari support
- Navigate and interact
- Screenshots
- JavaScript execution

**Use Cases**:
- Cross-browser testing
- Complex interactions
- Performance testing

**Configuration**:
```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@anthropic/server-playwright"]
  }
}
```

#### 12. **Git Server** (`@modelcontextprotocol/server-git`)

**Purpose**: Advanced git operations

**Capabilities**:
- Git status/diff/log
- Commit history analysis
- Branch management
- Change inspection

**Use Cases**:
- Analyzing commits
- Managing branches
- Reviewing changes
- Git automation

**Configuration**:
```json
{
  "git": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/CoomerDL"]
  }
}
```

#### 13. **Brave Search Server** (`@modelcontextprotocol/server-brave-search`)

**Purpose**: Web search for documentation and troubleshooting

**Capabilities**:
- Web search
- News search
- Image search

**Use Cases**:
- Finding documentation
- Researching new features
- Troubleshooting errors
- Discovering libraries

**Configuration**:
```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    }
  }
}
```

**Optional**: Requires `BRAVE_API_KEY` from [Brave Search API](https://brave.com/search/api/)

#### 14. **PostgreSQL Server** (`mcp-server-postgres`)

**Purpose**: PostgreSQL operations for future scaling

**Capabilities**:
- Execute queries
- Schema inspection
- Query analysis
- Performance tuning

**Use Cases**:
- Migration from SQLite
- Multi-user support
- Better concurrency
- Advanced features

**Configuration**:
```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "mcp-server-postgres"],
    "env": {
      "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
    }
  }
}
```

**Optional**: For future database migration

## Installation Guide

### Automated Setup

#### Unix/macOS
```bash
./scripts/mcp/setup.sh
```

#### Windows
```powershell
.\scripts\mcp\setup.ps1
```

### Manual Installation

#### npm-based servers (Node.js required)
```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @github/mcp-server
npm install -g @anthropic/server-puppeteer
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g mcp-server-docker
npm install -g mcp-server-yt-dlp
npm install -g @anthropic/server-playwright
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-brave-search
npm install -g mcp-server-postgres
```

#### Python-based servers (Python 3.8+ required)
```bash
pip install mcp-server-python-analysis
```

### Verification

```bash
./scripts/mcp/verify-installation.sh
```

## GitHub Repository Settings

To enable MCP servers for GitHub Copilot in the web UI:

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Copilot** → **MCP Servers**
3. Click **Add Server** or **Edit Configuration**
4. Copy the entire contents of `.github/copilot/mcp.json`
5. Paste and save

The configuration will be automatically available to all GitHub Copilot sessions.

## Environment Variables

Environment variables are configured differently for GitHub Copilot vs local development.

### For GitHub Copilot (Repository Secrets)

Add secrets via **Settings → Secrets and variables → Actions** with the `COPILOT_MCP_` prefix:

**Required:**
- `COPILOT_MCP_GITHUB_TOKEN`: Personal access token for GitHub API access
  - Scopes needed: `repo`, `read:org`, `workflow`
  - Create at: https://github.com/settings/tokens

**Optional:**
- `COPILOT_MCP_BRAVE_API_KEY`: API key for Brave Search
  - Get it at: https://brave.com/search/api/
- `COPILOT_MCP_POSTGRES_CONNECTION_STRING`: PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`

**Adding Repository Secrets:**
1. Navigate to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add name (e.g., `COPILOT_MCP_GITHUB_TOKEN`) and value
4. Click **Add secret**

### For Local Development (Shell Environment Variables)

Use standard variable names without the `COPILOT_MCP_` prefix:

**Required:**
- `GITHUB_TOKEN`: Personal access token for GitHub API access
- `PROJECT_PATH`: Automatically set to current directory by configs

**Optional:**
- `BRAVE_API_KEY`: API key for Brave Search
- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection string

#### Unix/macOS (Bash)
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export BRAVE_API_KEY="your_brave_key_here"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

#### Windows (PowerShell)
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
$env:BRAVE_API_KEY = "your_brave_key_here"
```

For persistence, use System Environment Variables in Control Panel.

## Usage Examples

### Example 1: Analyzing Database Performance

```
Agent prompt: "Analyze the downloads.db database and suggest optimizations"

The agent will:
1. Use SQLite server to list tables
2. Run EXPLAIN on slow queries
3. Suggest adding indexes
4. Provide migration SQL
```

### Example 2: Testing Web Scraper

```
Agent prompt: "Test the Coomer scraper with URL X"

The agent will:
1. Use Puppeteer to navigate to the URL
2. Use Fetch to get HTML content
3. Compare with scraper output
4. Identify any discrepancies
```

### Example 3: Type Checking

```
Agent prompt: "Run mypy on all Python files and fix type errors"

The agent will:
1. Use Python Analysis server to run mypy
2. Identify type errors
3. Use Filesystem server to read files
4. Fix type annotations
5. Re-run verification
```

### Example 4: Finding Similar Code

```
Agent prompt: "Find all places where we use threading.Event for cancellation"

The agent will:
1. Use GitHub server to search code
2. List all occurrences
3. Analyze patterns
4. Suggest standardization
```

## Troubleshooting

### Server Not Found

**Problem**: `npx: command not found` or server not accessible

**Solution**:
1. Ensure Node.js is installed: `node --version`
2. Ensure npm is installed: `npm --version`
3. Re-run setup script: `./scripts/mcp/setup.sh`

### Permission Errors

**Problem**: Permission denied when running scripts

**Solution**:
```bash
chmod +x scripts/mcp/*.sh
```

### GitHub Token Issues

**Problem**: GitHub server returns 401 Unauthorized

**Solution**:
1. Verify token is set: `echo $GITHUB_TOKEN`
2. Check token scopes on GitHub
3. Generate new token if needed

### Python Server Not Working

**Problem**: Python analysis server fails to start

**Solution**:
1. Check Python version: `python --version` (need 3.8+)
2. Reinstall: `pip install --upgrade mcp-server-python-analysis`
3. Verify module: `python -m mcp_server_python_analysis --help`

### Database Path Issues

**Problem**: SQLite server can't find downloads.db

**Solution**:
1. Verify database exists: `ls resources/config/downloads.db`
2. Use absolute path in configuration
3. Create database if missing (app creates it on first run)

## Configuration Files

- **`.github/copilot/mcp.json`**: GitHub Copilot MCP configuration
- **`.mcp/config.json`**: Local development MCP configuration
- **`.github/mcp/servers/*.json`**: Individual server configurations (modular)

## Scripts

- **`scripts/mcp/setup.sh`**: Automated setup for Unix/macOS
- **`scripts/mcp/setup.ps1`**: Automated setup for Windows
- **`scripts/mcp/start-servers.sh`**: Information about starting servers
- **`scripts/mcp/verify-installation.sh`**: Verify installation completeness

## Additional Resources

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [GitHub MCP Server](https://github.com/github/mcp-server)
- [CoomerDL Documentation](../../README.md)
- [MCP Setup Guide](../../MCP_SETUP_GUIDE.md)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Run verification script: `./scripts/mcp/verify-installation.sh`
3. Review logs from server startup
4. Open issue on GitHub: https://github.com/primoscope/CoomerDL/issues

---

**Last Updated**: 2026-01-13  
**MCP Version**: 1.0  
**Servers Configured**: 14
