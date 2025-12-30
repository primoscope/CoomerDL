# Quick Start Guide: Using AI Agents in CoomerDL

This guide shows you how to use the GitHub Copilot/Gemini AI agents configured in this repository.

## Prerequisites

1. Ensure you have GitHub Copilot or compatible AI assistant enabled
2. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/Emy69/CoomerDL.git
   cd CoomerDL
   pip install -r requirements.txt
   ```

## Available Agents

### 1. clever-coder (General Development)
**Use for**: Bug fixes, new features, general coding tasks

**Location**: `.github/agents/my-agent.agent.md`

**Capabilities**:
- Plans before implementing
- Explains decisions clearly
- Focuses on correctness and maintainability
- Suggests iterative improvements

**Example prompts**:
```
@clever-coder Fix the cancellation bug in downloader/bunkr.py

@clever-coder Implement the new batch download feature according to SPECIFICATIONS.md

@clever-coder Refactor the progress callback system to reduce UI updates
```

### 2. concurrency-expert (Threading & Async)
**Use for**: Thread safety issues, race conditions, concurrent operations

**Location**: `.github/agents/concurrency-expert.agent.md`

**Capabilities**:
- Identifies race conditions and deadlocks
- Implements thread-safe patterns
- Optimizes concurrent downloads
- Ensures graceful shutdown

**Example prompts**:
```
@concurrency-expert Review the thread safety of the cancel mechanism in all downloaders

@concurrency-expert Fix the database locking issue when multiple threads access the cache

@concurrency-expert Optimize the ThreadPoolExecutor usage in the download queue
```

### 3. performance-optimizer (Speed & Memory)
**Use for**: Performance bottlenecks, memory issues, optimization

**Location**: `.github/agents/performance-optimizer.agent.md`

**Capabilities**:
- Profiles code to find bottlenecks
- Implements algorithmic improvements
- Optimizes I/O operations
- Reduces memory usage

**Example prompts**:
```
@performance-optimizer Optimize the database query that's causing slow startup

@performance-optimizer Reduce memory usage in the progress callback system

@performance-optimizer Profile and improve download speed for large files
```

## Validation

Before starting, validate your setup:

```bash
# Validate agent configurations
python validate_agents.py

# Test installation
python test_installation.py

# Run test suite
pytest tests/ -v
```

All three commands should pass with ✅.

## Workflow Example

Let's say you want to fix a threading issue:

1. **Identify the task** in `ROADMAP.md` or `DEVELOPMENT_ROADMAP.md`
2. **Choose the right agent**: For threading → `concurrency-expert`
3. **Provide context**:
   ```
   @concurrency-expert 
   
   Task: Fix race condition in downloader/erome.py line 150
   
   Context:
   - Multiple threads are accessing self.cancel_flag without locking
   - This causes intermittent failures when canceling downloads
   - See CONTRACTS.md section on thread-safe cancellation
   
   Requirements:
   - Use threading.Event() pattern as shown in other downloaders
   - Maintain backward compatibility
   - Add test case to verify fix
   ```

4. **Review the agent's response**: The agent will provide:
   - Root cause analysis
   - Proposed solution
   - Implementation code
   - Test verification steps

5. **Test the fix**:
   ```bash
   python -m pytest tests/test_contracts.py::TestCancellationContract -v
   ```

6. **Iterate if needed**: Ask follow-up questions or request adjustments

## Best Practices

### DO ✅
- Reference specific files and line numbers
- Provide context from documentation (ROADMAP.md, SPECIFICATIONS.md, etc.)
- Specify acceptance criteria
- Ask for explanations when unclear
- Request tests along with implementation

### DON'T ❌
- Make vague requests without context
- Skip validation after changes
- Ignore agent warnings about risks
- Implement without understanding the changes
- Forget to run tests

## Task Priority

When working with agents, follow this priority:

1. **🔴 CRITICAL**: Bugs causing crashes or data loss
2. **🟠 HIGH**: Important features or significant bugs
3. **🟡 MEDIUM**: Improvements and optimizations
4. **🟢 LOW**: Nice-to-have features and cleanup

See `ROADMAP.md` for all tasks with priority markers.

## Common Scenarios

### Scenario 1: Fixing a Bug
```
@clever-coder

Read ROADMAP.md task BUG-003 about the filename sanitization issue.
The bug is in downloader/downloader.py around line 227.
Please:
1. Identify the root cause
2. Implement the fix using the existing sanitize_filename() pattern
3. Add a test case to prevent regression
```

### Scenario 2: Performance Issue
```
@performance-optimizer

The application takes 5+ seconds to start up. 
Profile the startup sequence and identify bottlenecks.
Focus on:
- Database initialization in downloader/downloader.py
- Config loading in app/settings_window.py
Target: <1 second startup time
```

### Scenario 3: Threading Problem
```
@concurrency-expert

Intermittent "database is locked" errors when running multiple downloads.
Files involved:
- downloader/downloader.py (database access)
- downloader/queue.py (queue management)
Implement proper locking strategy as per CONTRACTS.md
```

## Documentation References

- **Agent Details**: `.github/agents/README.md`
- **Workflow Guide**: `AI_AGENT_WORKFLOW.md`
- **Task List**: `ROADMAP.md`
- **Specifications**: `SPECIFICATIONS.md`
- **Code Contracts**: `tests/CONTRACTS.md`
- **Validation Report**: `AGENT_VALIDATION_REPORT.md`

## Troubleshooting

### "Agent not found" error
- Check that the agent file exists in `.github/agents/`
- Verify the agent name matches the `name:` field in the frontmatter
- Run `python validate_agents.py` to check configuration

### Agent gives generic responses
- Provide more specific context
- Reference specific files and line numbers
- Include relevant documentation sections
- Specify acceptance criteria clearly

### Changes break tests
- Run `pytest tests/ -v` to identify failures
- Review the failed test to understand what broke
- Ask the agent to fix while maintaining the contract
- Consider if the test itself needs updating

## Getting Help

If you encounter issues:

1. Check [AGENT_VALIDATION_REPORT.md](AGENT_VALIDATION_REPORT.md)
2. Review [AI_AGENT_WORKFLOW.md](AI_AGENT_WORKFLOW.md)
3. Join the [Discord Server](https://discord.gg/ku8gSPsesh)
4. Open an issue on [GitHub](https://github.com/Emy69/CoomerDL/issues)

---

**Ready to start?** Pick a task from `ROADMAP.md` and invoke the appropriate agent! 🚀
