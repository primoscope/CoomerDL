# AI Agent Quick Reference

**TL;DR**: This repository has 5 specialized AI agents + workflow documentation for optimal development.

## 🤖 Available Agents

| Agent | Use For | Files |
|-------|---------|-------|
| **clever-coder** | General coding, bug fixes, features | `.github/agents/my-agent.agent.md` |
| **performance-optimizer** | Speed/memory optimization | `.github/agents/performance-optimizer.agent.md` |
| **concurrency-expert** | Threading, race conditions | `.github/agents/concurrency-expert.agent.md` |
| **roadmap-manager** | Implement roadmap items, track progress, update docs | `.github/agents/roadmap-manager.agent.md` |
| **docs-verifier** | Verify documented features exist and work, fix mismatches | `.github/agents/docs-verifier.agent.md` |

## ⚡ Quick Start

```bash
# For bug fixes
@agent:clever-coder Fix BUG-001 in downloader.py line 227

# For performance
@agent:performance-optimizer Optimize PERF-001 database queries

# For threading issues
@agent:concurrency-expert Review thread safety in bunkr.py

# For implementing roadmap features
@agent:roadmap-manager Implement next high-priority feature from DEVELOPMENT_ROADMAP.md

# For verifying documentation accuracy
@agent:docs-verifier Verify all features in README.md are actually implemented and working
```

## 📚 Documentation

- **Workflows**: `AI_AGENT_WORKFLOW.md` - Step-by-step task patterns
- **Orchestration**: `.github/agents/ORCHESTRATION.md` - Multi-agent coordination
- **Prompts**: `.github/agents/PROMPT_OPTIMIZATION.md` - Writing effective prompts
- **MCP Servers**: `.github/mcp/README.md` - External tool integration

## 🎯 Task Routing

- `BUG-*` → clever-coder
- `PERF-*` → performance-optimizer  
- `REFACTOR-*` (threading) → concurrency-expert
- `FEATURE-*` → roadmap-manager (for roadmap features) or clever-coder (for ad-hoc features)
- Documentation verification → docs-verifier
- Roadmap implementation → roadmap-manager

## 🔧 Key Features

✅ **Thread-safe cancellation** - All downloaders use `threading.Event()`
✅ **DB optimization** - Indexed queries, no full preload
✅ **Progress throttling** - 90% fewer callbacks, smoother UI
✅ **Session reuse** - Connection pooling for faster downloads

## 📈 Performance Gains

- Startup: **60-80% faster**
- Memory: **-50-100MB**
- Downloads: **+30-50%** (JPG5)
- CPU: **-20-30%** (progress callbacks)

## 🚀 Next Steps

1. Review `ROADMAP.md` for available tasks
2. Choose task based on priority (🔴 CRITICAL → 🟢 LOW)
3. Use appropriate agent via `@agent:name`
4. Follow workflow in `AI_AGENT_WORKFLOW.md`
