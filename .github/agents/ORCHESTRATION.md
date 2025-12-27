# Agent Orchestration Configuration

This file defines how multiple AI agents collaborate on CoomerDL tasks.

## Agent Roles and Specializations

### Primary Agents

1. **clever-coder** (`.github/agents/my-agent.agent.md`)
   - **Role**: General-purpose coding, bug fixes, feature implementation
   - **Strengths**: Planning, code correctness, maintainability
   - **When to use**: Default agent for most tasks
   - **Tools**: read, search, edit, execute

2. **performance-optimizer** (`.github/agents/performance-optimizer.agent.md`)
   - **Role**: Performance analysis and optimization
   - **Strengths**: Profiling, benchmarking, algorithmic improvements
   - **When to use**: PERF-* tasks, slow functions, memory issues
   - **Tools**: read, search, edit, execute, profile

3. **concurrency-expert** (`.github/agents/concurrency-expert.agent.md`)
   - **Role**: Thread safety, async patterns, race condition fixes
   - **Strengths**: Threading, locking, deadlock prevention
   - **When to use**: REFACTOR-* with threading, race conditions, deadlocks
   - **Tools**: read, search, edit, execute

## Orchestration Patterns

### Pattern 1: Sequential Handoff

**Use when**: Tasks have clear dependencies

**Example**: Database Optimization
```
1. clever-coder: Analyze current DB usage → identify bottleneck
2. performance-optimizer: Profile queries → measure baseline
3. clever-coder: Implement index → add schema changes
4. performance-optimizer: Benchmark after → verify improvement
```

**Workflow**:
```yaml
task: PERF-001 Database Indexing
agents:
  - agent: clever-coder
    role: analysis
    output: bottleneck_report.md
    
  - agent: performance-optimizer
    role: baseline
    input: bottleneck_report.md
    output: baseline_metrics.json
    
  - agent: clever-coder
    role: implement
    input: baseline_metrics.json
    output: code_changes
    
  - agent: performance-optimizer
    role: validate
    input: code_changes
    output: improvement_report.md
```

### Pattern 2: Parallel Review

**Use when**: Multiple perspectives needed

**Example**: Refactoring Review
```
Parallel:
  - clever-coder: Check code correctness, maintainability
  - concurrency-expert: Check thread safety, race conditions
  - performance-optimizer: Check performance implications

Synthesis:
  - clever-coder: Integrate feedback, make final changes
```

**Workflow**:
```yaml
task: REFACTOR-001 Standardize Cancellation
review_parallel:
  - agent: clever-coder
    focus: correctness
  - agent: concurrency-expert
    focus: thread_safety
  - agent: performance-optimizer
    focus: overhead

synthesis:
  agent: clever-coder
  input: all_reviews
  output: final_implementation
```

### Pattern 3: Iterative Refinement

**Use when**: Optimization requires multiple attempts

**Example**: Performance Tuning
```
Loop until target met:
  1. performance-optimizer: Profile → identify next bottleneck
  2. clever-coder: Implement fix
  3. performance-optimizer: Measure → check if target met
```

**Workflow**:
```yaml
task: Optimize startup time to < 1 second
target: startup_time < 1.0s
max_iterations: 5

iterations:
  - iteration: 1
    agent: performance-optimizer
    action: profile
    result: "DB load takes 4.2s (bottleneck)"
    
  - iteration: 2
    agent: clever-coder
    action: implement
    change: "Add DB index"
    
  - iteration: 3
    agent: performance-optimizer
    action: measure
    result: "startup_time = 1.8s (not met)"
    
  - iteration: 4
    agent: clever-coder
    action: implement
    change: "Remove full cache preload"
    
  - iteration: 5
    agent: performance-optimizer
    action: measure
    result: "startup_time = 0.9s (TARGET MET!)"
```

## Task Assignment Rules

### Automatic Assignment

Based on task prefix:
- `BUG-*` → **clever-coder**
- `PERF-*` → **performance-optimizer**
- `REFACTOR-*` with "thread" or "lock" → **concurrency-expert**
- `REFACTOR-*` other → **clever-coder**
- `FEATURE-*` → **clever-coder**
- `ARCH-*` → **clever-coder** (with consultation from others)

### Manual Override

```yaml
# In task comment:
# @agent:performance-optimizer
# This forces specific agent regardless of prefix
```

## Communication Protocol

### Agent-to-Agent

Agents communicate via structured artifacts:

**Performance Report**:
```json
{
  "agent": "performance-optimizer",
  "task": "PERF-001",
  "baseline": {
    "metric": "startup_time",
    "value": 5.3,
    "unit": "seconds"
  },
  "bottleneck": {
    "location": "downloader.py:load_download_cache()",
    "cause": "Full table scan of 10k rows"
  },
  "recommendation": "Add index on media_url column"
}
```

**Concurrency Report**:
```json
{
  "agent": "concurrency-expert",
  "task": "REFACTOR-001",
  "issues_found": [
    {
      "type": "race_condition",
      "location": "bunkr.py:26",
      "severity": "high",
      "description": "Boolean flag not thread-safe"
    }
  ],
  "recommendations": [
    "Replace with threading.Event()"
  ]
}
```

### Agent-to-Human

Use standardized output format:

```markdown
## Task: PERF-001 Database Optimization

**Agent**: performance-optimizer  
**Status**: Complete ✅

### Changes Made
- Added index on `downloads.media_url`
- Removed full cache preload
- Implemented on-demand lookup

### Results
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Startup Time | 5.3s | 0.9s | **83% faster** |
| Memory Usage | 120MB | 25MB | **79% reduction** |

### Validation
✅ All downloads still work
✅ Duplicate detection functional
✅ No regressions in tests

### Next Steps
Consider implementing LRU cache for frequently accessed URLs
```

## Conflict Resolution

When agents disagree:

1. **Performance vs. Correctness**
   - Priority: Correctness first
   - Arbiter: clever-coder
   - Resolution: Implement correct solution, then optimize

2. **Complexity vs. Maintainability**
   - Priority: Maintainability
   - Arbiter: clever-coder
   - Resolution: Choose simpler approach unless performance critical

3. **Thread Safety vs. Performance**
   - Priority: Thread safety
   - Arbiter: concurrency-expert
   - Resolution: Safe first, then optimize if needed

## Quality Gates

All agents must pass:

### Gate 1: Correctness
- Code compiles/runs
- Existing tests pass
- No new errors introduced

### Gate 2: Performance
- No regressions (>10% slowdown)
- Improvements verified with benchmarks
- Memory usage within bounds

### Gate 3: Safety
- No race conditions
- Proper resource cleanup
- Secure against common vulnerabilities

### Gate 4: Maintainability
- Code is readable
- Changes are documented
- Follows project conventions

## Optimization Workflow

Standard flow for optimization tasks:

```
┌─────────────────────────────────────────────────┐
│ 1. ANALYZE (performance-optimizer)              │
│    - Profile current code                       │
│    - Identify bottlenecks                       │
│    - Measure baseline                           │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ 2. PLAN (clever-coder)                          │
│    - Design optimization strategy               │
│    - Consider correctness implications          │
│    - Identify risks                             │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ 3. REVIEW SAFETY (concurrency-expert)           │
│    - Check for threading issues                 │
│    - Validate locking strategy                  │
│    - Approve or suggest changes                 │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ 4. IMPLEMENT (clever-coder)                     │
│    - Write optimized code                       │
│    - Add tests                                  │
│    - Document changes                           │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ 5. VALIDATE (performance-optimizer)             │
│    - Benchmark new code                         │
│    - Compare to baseline                        │
│    - Verify no regressions                      │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ 6. VERIFY (concurrency-expert)                  │
│    - Stress test under load                     │
│    - Check for race conditions                  │
│    - Confirm clean shutdown                     │
└────────────────┬────────────────────────────────┘
                 │
                 v
              SUCCESS ✅
```

## Best Practices

1. **Clear Handoffs**: Each agent documents what they did and what's next
2. **Preserve Context**: Pass relevant files/reports to next agent
3. **Explicit Goals**: Define success criteria before starting
4. **Measure Everything**: Baseline → Change → Validate
5. **Incremental Progress**: Small, verified steps
6. **Document Decisions**: Why this approach was chosen
7. **Learn from Failures**: Document what didn't work and why

## Examples

See `AI_AGENT_WORKFLOW.md` for detailed workflow patterns and examples.

## Future Enhancements

- **Agent voting**: Multiple agents vote on best approach
- **Automated testing**: Agents trigger test suites automatically
- **Continuous optimization**: Agents monitor metrics and suggest improvements
- **Learning feedback**: Agents learn from past successful/failed optimizations
