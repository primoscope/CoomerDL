# MCP Server Configuration for CoomerDL

This directory contains MCP (Model Context Protocol) server configurations for enhancing AI agent capabilities when working on CoomerDL.

## What is MCP?

MCP is a protocol that allows AI agents to access external tools, data sources, and services through standardized server interfaces. This enables agents to:

- Access specialized tools beyond basic file operations
- Query external data sources
- Integrate with development tools and APIs
- Maintain context across sessions

## MCP Servers for CoomerDL

### 1. GitHub MCP Server (Installed)

**Purpose**: Enhanced GitHub repository interaction

**Capabilities**:
- Read/search code across the repository
- Access PR reviews and comments
- Query GitHub Actions workflow results
- Search issues and discussions

**Usage**: Automatically available to agents through GitHub Copilot integration

### 2. Python Analysis MCP Server (Recommended)

**Purpose**: Advanced Python code analysis

**Capabilities**:
- Static type checking (mypy integration)
- Complexity analysis (cyclomatic complexity, cognitive complexity)
- Import graph analysis
- Dependency vulnerability scanning
- Performance profiling data access

**Installation**:
```bash
# Install the Python analysis MCP server
pip install mcp-server-python-analysis

# Configure in your MCP settings
{
  "mcpServers": {
    "python-analysis": {
      "command": "python",
      "args": ["-m", "mcp_server_python_analysis"],
      "env": {
        "PROJECT_PATH": "/home/runner/work/CoomerDL/CoomerDL"
      }
    }
  }
}
```

### 3. SQLite MCP Server (Recommended for DB optimization)

**Purpose**: Direct database inspection and optimization

**Capabilities**:
- Query execution and analysis
- Index recommendation
- Query plan analysis (EXPLAIN)
- Schema inspection
- Performance statistics

**Installation**:
```bash
pip install mcp-server-sqlite

# Configuration
{
  "mcpServers": {
    "sqlite": {
      "command": "mcp-server-sqlite",
      "args": ["--db-path", "resources/config/downloads.db"]
    }
  }
}
```

## Configuration

Create `.mcp/config.json` in repository root:

```json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "python-analysis": {
      "command": "python",
      "args": ["-m", "mcp_server_python_analysis"],
      "env": {
        "PROJECT_PATH": "${PROJECT_ROOT}"
      }
    },
    "sqlite": {
      "command": "mcp-server-sqlite",
      "args": ["--db-path", "resources/config/downloads.db"],
      "readonly": false
    }
  }
}
```

## Resources

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/github)
