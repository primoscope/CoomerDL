# MCP Integration Guide for AI Agents

This document provides guidance for AI agents working on CoomerDL on how to effectively leverage the configured MCP (Model Context Protocol) servers.

## Available MCP Servers

CoomerDL has 14+ MCP servers configured and ready to use. They are automatically available to all agents working on this repository.

### Quick Reference

| Server | Primary Use | Command |
|--------|-------------|---------|
| **filesystem** | Read/write files | File operations |
| **sqlite** | Database access | Query downloads.db |
| **github** | Repository operations | Search code, PRs, issues |
| **python-analysis** | Type checking, analysis | mypy, complexity metrics |
| **puppeteer** | Browser automation | Test scrapers |
| **fetch** | HTTP requests | Test APIs, endpoints |
| **memory** | Persistent context | Remember decisions |
| **sequential-thinking** | Complex reasoning | Multi-step analysis |
| **docker** | Container ops | Test in isolation |
| **yt-dlp** | Video download testing | Test ytdlp adapter |
| **playwright** | Multi-browser testing | Cross-browser tests |
| **git** | Advanced git ops | History, branches |
| **brave-search** | Web search | Find docs, solutions |
| **postgres** | PostgreSQL | Future migration |

## When to Use Each Server

### filesystem Server
**Use when**: Reading/writing code, configs, or data files

**Examples**:
- "Read the downloader/base.py file"
- "Create a new scraper in downloader/newscraper.py"
- "List all files in the app/gui/ directory"
- "Search for all files containing 'download_file'"

**Capabilities**:
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_directory` - List directory contents
- `create_directory` - Create directories
- `move_file` - Rename/move files
- `search_files` - Find files by pattern

### sqlite Server
**Use when**: Working with downloads.db database

**Examples**:
- "Show me the schema of the job_history table"
- "Find all failed downloads in the last 7 days"
- "Run EXPLAIN on the download tracking query"
- "Suggest indexes to improve query performance"
- "Count how many downloads have status 'completed'"

**Capabilities**:
- `execute_query` - Run SQL queries (SELECT, INSERT, UPDATE, DELETE)
- `read_query` - Read-only queries
- `list_tables` - Show all tables
- `describe_table` - Show table schema
- `analyze_query` - Get query execution plan (EXPLAIN)

**Database Location**: `resources/config/downloads.db`

**Common Tables**:
- `job_history` - Download job tracking
- `download_cache` - Duplicate detection cache
- `events` - Download events and progress

### github Server
**Use when**: Searching code, analyzing PRs, checking CI/CD

**Examples**:
- "Find all uses of threading.Event in the codebase"
- "Show me recent PRs related to download performance"
- "Check the status of GitHub Actions for the last commit"
- "Search for TODO comments in Python files"
- "List all open issues tagged with 'bug'"

**Capabilities**:
- `search_code` - Search repository code
- `search_repositories` - Find repos
- `get_file_contents` - Fetch file from GitHub
- `list_commits` - Show commit history
- `list_issues` - List/search issues
- `create_issue` - Create new issue
- `list_pull_requests` - List PRs
- `get_workflow_runs` - Check CI/CD status

**Required**: `GITHUB_TOKEN` environment variable

### python-analysis Server
**Use when**: Type checking, code quality, complexity analysis

**Examples**:
- "Run mypy on downloader/queue.py"
- "Calculate cyclomatic complexity for all functions in base.py"
- "Show import dependencies for the downloader module"
- "Find functions with complexity > 10"
- "Check for type errors in the entire codebase"

**Capabilities**:
- `type_check` - Run mypy static type checking
- `complexity_analysis` - Calculate complexity metrics
- `import_graph` - Analyze module dependencies
- `dependency_scan` - Check for vulnerable dependencies
- `code_metrics` - Get code quality metrics

**Installation**: `pip install mcp-server-python-analysis`

### puppeteer Server
**Use when**: Testing web scrapers, debugging browser interactions

**Examples**:
- "Navigate to https://coomer.su/onlyfans/user/example"
- "Test if the Coomer scraper can extract post data from this page"
- "Take a screenshot of the SimpCity post page"
- "Check if cookie authentication is working"
- "Debug why JavaScript content isn't loading"

**Capabilities**:
- `navigate_url` - Go to URL
- `click_element` - Click on element
- `fill_form` - Fill form fields
- `take_screenshot` - Capture screenshot
- `execute_javascript` - Run JS in page
- `wait_for_selector` - Wait for element

**Use Cases**:
- Testing scrapers on live sites
- Debugging JavaScript-heavy pages
- Validating cookie extraction
- Testing authentication flows

### fetch Server
**Use when**: Testing HTTP endpoints, debugging API responses

**Examples**:
- "Fetch the HTML from https://example.com/post/123"
- "Get JSON response from the Coomer API"
- "Test if the download URL is accessible"
- "Check HTTP headers from the Bunkr CDN"
- "Validate the redirect chain for this URL"

**Capabilities**:
- `fetch_url` - Fetch any URL
- `fetch_html` - Get HTML content
- `fetch_json` - Get JSON response
- `fetch_text` - Get text content

**Use Cases**:
- Testing API endpoints
- Debugging HTTP responses
- Validating URL patterns
- Inspecting headers

### memory Server
**Use when**: Maintaining context across sessions

**Examples**:
- "Remember that we use exponential backoff for rate limiting"
- "Store the decision to use threading.Event for cancellation"
- "Recall architectural decisions about the factory pattern"
- "What patterns have we learned about download optimization?"

**Capabilities**:
- `store_entity` - Store facts
- `retrieve_entities` - Get stored facts
- `create_relation` - Link entities
- `query_graph` - Query knowledge

**Use Cases**:
- Remember architectural decisions
- Track learned patterns
- Maintain project context
- Store debugging insights

### sequential-thinking Server
**Use when**: Complex multi-step reasoning needed

**Examples**:
- "Analyze the race condition in the download queue"
- "Design a new scraper architecture for better maintainability"
- "Debug why downloads sometimes hang indefinitely"
- "Optimize the database query performance systematically"

**Capabilities**:
- `think_step_by_step` - Structured reasoning
- `break_down_problem` - Problem decomposition
- `reason_about_code` - Code analysis

**Use Cases**:
- Architectural decisions
- Debugging complex issues
- Algorithm optimization
- Design patterns

### docker Server
**Use when**: Testing in containers, creating reproducible builds

**Examples**:
- "Create a Docker container to test CoomerDL with Python 3.9"
- "Run the test suite in an isolated environment"
- "Build a production Docker image"
- "Test installation on a fresh Ubuntu system"

**Capabilities**:
- `list_containers` - List containers
- `create_container` - Create new container
- `start_container` - Start container
- `stop_container` - Stop container
- `exec_command` - Run command in container
- `inspect_container` - Get container details

### yt-dlp Server
**Use when**: Testing yt-dlp integration, debugging video downloads

**Examples**:
- "Extract info from this YouTube URL"
- "List available formats for this video"
- "Compare our yt-dlp adapter output with native yt-dlp"
- "Test subtitle extraction"

**Capabilities**:
- `extract_info` - Get video metadata
- `get_formats` - List available formats
- `download_video` - Download video
- `get_subtitles` - Get subtitle tracks

**Use Cases**:
- Testing ytdlp_adapter.py
- Validating format selection
- Debugging download issues
- Comparing implementations

### playwright Server
**Use when**: Cross-browser testing needed

**Examples**:
- "Test the scraper in Firefox and Chrome"
- "Check if the site works in Safari"
- "Run browser performance tests"
- "Test mobile viewport rendering"

**Capabilities**:
- Multi-browser support (Chrome, Firefox, Safari)
- Same as Puppeteer but with better browser coverage

### git Server
**Use when**: Advanced git operations needed

**Examples**:
- "Show git diff for uncommitted changes"
- "List commits in the last 7 days"
- "Analyze commit history for file X"
- "Show branches containing commit ABC123"

**Capabilities**:
- `git_status` - Check status
- `git_diff` - Show differences
- `git_log` - Show history
- `git_show` - Show commit details
- `git_commit` - Create commit
- `git_branch` - Branch operations

### brave-search Server
**Use when**: Need to find documentation or research solutions

**Examples**:
- "Search for Python threading best practices"
- "Find documentation for yt-dlp format selection"
- "Look up SQLite index optimization techniques"
- "Research how other download managers handle cancellation"

**Capabilities**:
- `web_search` - Search the web
- `search_news` - Search news
- `search_images` - Search images

**Required**: `BRAVE_API_KEY` environment variable (optional)

### postgres Server
**Use when**: Planning PostgreSQL migration (future)

**Examples**:
- "Design PostgreSQL schema for migration from SQLite"
- "Compare query performance between SQLite and PostgreSQL"
- "Plan migration strategy"

**Required**: `POSTGRES_CONNECTION_STRING` (optional, for future use)

## Best Practices for Agents

### 1. Choose the Right Server

**Do**: Use specialized servers for their intended purpose
```
✅ "Use sqlite server to query downloads.db"
✅ "Use puppeteer to test the scraper"
✅ "Use python-analysis to run mypy"
```

**Don't**: Use generic approaches when specialized servers exist
```
❌ "Read the database file as text"
❌ "Parse HTML manually when puppeteer can render it"
❌ "Run mypy via bash when python-analysis server exists"
```

### 2. Combine Servers Effectively

**Example 1**: Database optimization
```
1. Use sqlite server to list tables
2. Use sqlite server to run EXPLAIN on slow query
3. Use filesystem server to read the Python code using that query
4. Use python-analysis to check if the code is type-safe
5. Use filesystem server to write optimized version
```

**Example 2**: Scraper debugging
```
1. Use puppeteer to navigate to the target URL
2. Use fetch to get raw HTML
3. Use filesystem to read scraper code
4. Compare scraper output with actual page content
5. Use github to search for similar scraper patterns
```

### 3. Use Memory for Context

Store important information that should persist:
```
✅ "Remember: We use threading.Event for cancellation"
✅ "Store: Factory pattern with can_handle() classmethods"
✅ "Note: SQLite queries must be indexed for performance"
```

### 4. Leverage GitHub Server for Code Search

Instead of reading every file:
```
✅ "Use github server to search for 'download_file' function"
✅ "Find all files that import queue.py"
❌ "Read every file looking for the function"
```

### 5. Use Sequential Thinking for Complex Problems

For architectural decisions or complex debugging:
```
✅ "Use sequential-thinking to analyze the race condition"
✅ "Break down the performance problem step by step"
```

## Common Workflows

### Workflow 1: Adding a New Scraper

1. **Research**: Use brave-search to find info about the target site
2. **Analysis**: Use puppeteer to inspect the site structure
3. **Implementation**: Use filesystem to create new scraper file
4. **Testing**: Use fetch to test API endpoints
5. **Validation**: Use python-analysis to check types
6. **Integration**: Use github to search for similar patterns

### Workflow 2: Database Performance Optimization

1. **Inspection**: Use sqlite server to list tables and indexes
2. **Analysis**: Use sqlite server to run EXPLAIN on slow queries
3. **Code Review**: Use filesystem to read Python code
4. **GitHub Search**: Use github to find similar query patterns
5. **Implementation**: Use filesystem to write optimized queries
6. **Validation**: Use sqlite server to verify improvements

### Workflow 3: Debugging a Scraper

1. **Live Test**: Use puppeteer to navigate to problem URL
2. **HTML Inspection**: Use fetch to get raw HTML
3. **Code Analysis**: Use filesystem to read scraper code
4. **Pattern Search**: Use github to find similar issues
5. **Fix Implementation**: Use filesystem to update code
6. **Type Check**: Use python-analysis to verify changes

### Workflow 4: Code Quality Review

1. **Type Checking**: Use python-analysis to run mypy
2. **Complexity Analysis**: Use python-analysis for complexity metrics
3. **Code Search**: Use github to find duplicated patterns
4. **Refactoring**: Use filesystem to implement changes
5. **Validation**: Re-run python-analysis to verify

## Environment Setup

Some servers require environment variables:

```bash
# Required for GitHub server
export GITHUB_TOKEN="ghp_your_token_here"

# Optional for Brave search
export BRAVE_API_KEY="your_brave_key_here"

# Optional for PostgreSQL (future)
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:port/db"
```

## Troubleshooting

### Server Not Responding

If a server doesn't respond:
1. Check if it's installed: `npx -y <server-package> --help`
2. Verify environment variables are set
3. Try a simpler query to test connectivity
4. Fall back to alternative approaches

### Database Locked

If SQLite reports "database is locked":
1. Close CoomerDL application if running
2. Check for other processes accessing the DB
3. Use read-only mode if possible

### GitHub API Rate Limits

If GitHub server hits rate limits:
1. Verify GITHUB_TOKEN is set (higher limits with auth)
2. Reduce frequency of API calls
3. Use local git/filesystem servers instead

### Browser Automation Issues

If Puppeteer/Playwright fails:
1. Check if the site blocks automation
2. Try with different user agents
3. Use fetch server for simpler cases
4. Consider rate limiting

## Security Considerations

### Do Not:
- ❌ Store sensitive tokens in code or configs
- ❌ Share GITHUB_TOKEN or API keys
- ❌ Commit credentials to repository
- ❌ Log sensitive data in debug output

### Do:
- ✅ Use environment variables for secrets
- ✅ Use `${VARIABLE}` placeholders in configs
- ✅ Keep tokens secure and rotate regularly
- ✅ Use read-only access when possible

## Additional Resources

- **Full MCP Documentation**: `.github/mcp/README.md`
- **Setup Guide**: `MCP_SETUP_GUIDE.md`
- **Individual Server Configs**: `.github/mcp/servers/*.json`
- **MCP Specification**: https://github.com/modelcontextprotocol/specification

## Feedback

If you discover new use cases or best practices for MCP servers, please:
1. Document them in this file
2. Share examples in code reviews
3. Update agent prompts with learned patterns
4. Contribute to the project documentation

---

**For Agents**: This document is your guide to using the powerful MCP infrastructure. Use these servers to be more effective and deliver better results faster. Remember: specialized servers are always better than generic approaches.
