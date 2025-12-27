# AI Agent Prompt Optimization Guide

Guidelines for creating high-quality, effective prompts for AI agents working on CoomerDL.

## Core Principles

### 1. Specificity Over Generality
**❌ Vague**: "Fix the download issue"
**✅ Specific**: "Fix BUG-003: Variable 'response' referenced before assignment in bunkr.py line 126 when download fails"

### 2. Context + Goal + Constraints
**❌ Missing context**: "Add caching"
**✅ Complete**: "Add LRU caching (max 1000 entries) to is_url_downloaded() in downloader.py to reduce DB queries during bulk downloads. Must remain thread-safe."

### 3. Measurable Success Criteria
**❌ Vague success**: "Make it faster"
**✅ Measurable**: "Reduce startup time from 5.3s to <2s measured with time.time() around app initialization"

### 4. Explicit Safety Requirements
**❌ Implicit**: "Parallelize the downloads"
**✅ Explicit**: "Parallelize downloads using ThreadPoolExecutor with max_workers=5. Ensure cancel_event is checked in each worker. Maintain existing error handling."

## Prompt Templates

### Template 1: Bug Fix
```markdown
**Task**: Fix [BUG-ID]: [Brief description]

**Problem**:
- File: [path/to/file.py]
- Line: [line number]
- Error: [error message or description]
- Trigger: [steps to reproduce]

**Expected Behavior**:
[What should happen instead]

**Constraints**:
- Must not break [existing functionality]
- Must maintain [performance/safety requirement]
- Must follow [coding pattern]

**Acceptance Criteria**:
- [ ] Error no longer occurs
- [ ] [Related test] passes
- [ ] No new errors introduced
```

**Example**:
```markdown
**Task**: Fix BUG-001: Undefined variable log_message

**Problem**:
- File: downloader/downloader.py
- Line: 227
- Error: NameError: name 'log_message' is not defined
- Trigger: When server returns 429 status code

**Expected Behavior**:
Should log "Server error 429, retrying..." message

**Constraints**:
- Must use self.tr() for translation support
- Must follow existing log() call pattern
- Must not change error handling flow

**Acceptance Criteria**:
- [ ] Variable defined before use
- [ ] Message properly translated
- [ ] Test with rate-limited URL
```

### Template 2: Performance Optimization
```markdown
**Task**: Optimize [PERF-ID]: [Target metric]

**Current State**:
- Metric: [metric name]
- Current value: [measured value]
- Bottleneck: [identified cause]
- Measurement method: [how it was measured]

**Target**:
- Goal: [target value]
- Minimum acceptable: [threshold]

**Approach**:
- Strategy: [algorithmic/caching/parallel/other]
- Changes to: [files/functions affected]
- Risks: [potential issues]

**Validation**:
- [ ] Baseline measured
- [ ] Optimization implemented
- [ ] New metric measured
- [ ] Improvement ≥ [X%]
- [ ] No correctness regressions
```

**Example**:
```markdown
**Task**: Optimize PERF-001: Database lookup performance

**Current State**:
- Metric: Startup time
- Current value: 5.3 seconds
- Bottleneck: load_download_cache() loads entire downloads table (10k rows, 80MB)
- Measurement method: time.time() around ImageDownloaderApp() initialization

**Target**:
- Goal: <1 second startup
- Minimum acceptable: <2 seconds

**Approach**:
- Strategy: On-demand indexed queries instead of full preload
- Changes to: downloader/downloader.py (load_download_cache, is_url_downloaded)
- Risks: Increased query latency per lookup (mitigated by indexes)

**Validation**:
- [ ] Baseline: 5.3s measured
- [ ] Add index on media_url
- [ ] Implement is_url_downloaded() method
- [ ] Replace cache checks with DB queries
- [ ] New startup: <2s
- [ ] Downloads still skip duplicates correctly
```

### Template 3: Feature Implementation
```markdown
**Task**: Implement [FEATURE-ID]: [Feature name]

**Goal**:
[1-2 sentences describing what the feature does]

**Requirements**:
- Must [requirement 1]
- Must [requirement 2]
- Should [nice-to-have]

**Design**:
- UI changes: [describe]
- Backend changes: [describe]
- Data model: [describe]

**Integration Points**:
- Modifies: [existing components]
- Uses: [existing APIs/patterns]
- Affects: [other features]

**Testing**:
- [ ] Unit test: [test case]
- [ ] Integration test: [test case]
- [ ] Manual test: [test steps]

**Documentation**:
- [ ] Update README if public-facing
- [ ] Add docstrings to new functions
- [ ] Comment complex logic
```

### Template 4: Refactoring
```markdown
**Task**: Refactor [REFACTOR-ID]: [What is being refactored]

**Current Problem**:
- Code smell: [what's wrong]
- Impact: [why it matters]
- Location: [files/modules]

**Proposed Solution**:
- Pattern: [design pattern or approach]
- Structure: [new organization]
- Benefits: [improvements]

**Migration Plan**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Safety**:
- [ ] No breaking changes to public API
- [ ] All tests still pass
- [ ] Behavior unchanged
- [ ] Performance not degraded
```

## Prompt Enhancements

### Add Examples
```markdown
**Task**: Implement batch URL input

**Example Input**:
```
https://site1.com/post1
https://site2.com/post2
https://site1.com/post3
```

**Expected Behavior**:
- Parse 3 URLs
- Start 3 separate downloads
- Show progress for each
```

### Include Edge Cases
```markdown
**Task**: Validate URL input

**Edge Cases to Handle**:
1. Empty input → Show error "URL required"
2. Invalid URL (no protocol) → Show error "Invalid URL format"
3. Unsupported site → Show error "Site not supported"
4. Multiple URLs with blank lines → Ignore blank lines
5. Duplicate URLs → Only download once
```

### Specify Error Handling
```markdown
**Task**: Implement file download with retry

**Error Scenarios**:
1. Network timeout → Retry up to 3 times with exponential backoff
2. HTTP 429 (rate limit) → Wait [Retry-After] seconds, then retry
3. HTTP 404 → Log error, skip file, continue with others
4. Disk full → Show error dialog, stop download
5. User cancellation → Clean up partial files, stop gracefully
```

## Optimization-Specific Prompts

### For performance-optimizer Agent
```markdown
**Analysis Request**:
Profile the [function_name] function in [file_path]

**Focus Areas**:
- Time complexity
- Memory usage
- I/O operations
- Lock contention

**Output Format**:
1. Baseline metrics (time, memory, calls)
2. Hotspots (top 5 time consumers)
3. Recommendations (ranked by impact)
4. Expected improvements (% gains)
```

### For concurrency-expert Agent
```markdown
**Safety Review**:
Review [file_path] for concurrency issues

**Check For**:
- Race conditions on shared state
- Deadlock potential (lock ordering)
- Thread leaks (unclosed threads)
- Cancellation propagation
- Resource cleanup on error

**Risk Assessment**:
- Critical: Correctness bugs
- High: Data corruption potential
- Medium: Performance degradation
- Low: Code clarity issues
```

## Anti-Patterns to Avoid

### ❌ Too Broad
"Optimize the application"
→ Which part? What metric? What's the baseline?

### ❌ Missing Constraints
"Add parallel processing"
→ How many threads? What about thread safety? Cancellation?

### ❌ No Success Criteria
"Make the UI better"
→ What's wrong with it? What's "better"? How to measure?

### ❌ Implicit Assumptions
"Use asyncio for downloads"
→ Why asyncio vs threads? What about existing code? Migration path?

### ❌ No Context
"Fix line 100"
→ Which file? What's broken? What should it do?

## Quality Checklist

Before submitting a prompt, verify:

- [ ] **Specific**: Exact file, function, line number
- [ ] **Measurable**: Quantified goals and success criteria
- [ ] **Achievable**: Scoped to agent capabilities
- [ ] **Relevant**: Addresses real problem
- [ ] **Time-bound**: Priority/urgency clear
- [ ] **Context**: Background information provided
- [ ] **Constraints**: Limitations stated
- [ ] **Examples**: Expected behavior shown
- [ ] **Safety**: Thread safety, error handling specified
- [ ] **Testing**: Validation steps included

## Prompt Refinement Process

### Initial Prompt (Draft)
"Add caching to the downloader"

### Refinement 1: Add Specificity
"Add URL caching to downloader.py to avoid duplicate downloads"

### Refinement 2: Add Metrics
"Add URL caching to downloader.py to reduce duplicate DB queries from 100/sec to <10/sec during bulk downloads"

### Refinement 3: Add Implementation Details
"Add LRU cache (max 1000 entries) to is_url_downloaded() in downloader.py to reduce duplicate DB queries from 100/sec to <10/sec during bulk downloads. Must be thread-safe."

### Final Prompt
```markdown
**Task**: Implement URL caching for duplicate detection

**Problem**:
During bulk downloads (1000+ files), is_url_downloaded() makes 100 DB queries/sec, causing 30% CPU usage from DB overhead.

**Solution**:
Add LRU cache (max 1000 entries) to is_url_downloaded() method

**Requirements**:
- Cache size: 1000 most recent URLs
- Thread-safe: Use threading.Lock()
- Cache invalidation: On new download completion
- Maintain existing behavior: Cache miss → DB query

**Implementation**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def is_url_downloaded_cached(self, media_url):
    return self.is_url_downloaded(media_url)
```

**Validation**:
- [ ] Baseline: Profile DB query rate (100/sec)
- [ ] Implement cache
- [ ] Measure: Cache hit rate >90%, query rate <10/sec
- [ ] Test: Concurrent access safe
- [ ] Test: Cache invalidates on new downloads
```

## Advanced Techniques

### Chain-of-Thought Prompting
```markdown
**Task**: Optimize database query

**Think through**:
1. What is the current query complexity? → O(n) table scan
2. Why is it slow? → No index on WHERE clause column
3. What's the solution? → Add index
4. What are the tradeoffs? → Faster reads, slower writes (acceptable)
5. How to implement safely? → CREATE INDEX IF NOT EXISTS
6. How to verify? → EXPLAIN QUERY PLAN before/after
```

### Few-Shot Learning
```markdown
**Task**: Add error handling to download function

**Pattern** (from similar code):
```python
# In downloader.py:safe_request()
try:
    response = self.session.get(url)
    response.raise_for_status()
    return response
except requests.exceptions.Timeout:
    self.log(f"Timeout: {url}")
    return None
except requests.exceptions.RequestException as e:
    self.log(f"Error: {url} - {e}")
    return None
```

**Apply to**: download_file() in bunkr.py line 78
```

## Continuous Improvement

### Collect Metrics
Track prompt effectiveness:
- Time to completion
- Number of revisions needed
- Quality of output
- Agent satisfaction rating

### Iterate on Templates
Based on outcomes:
- What worked? → Codify in template
- What failed? → Add to anti-patterns
- What was unclear? → Add more examples

### Share Learnings
Document successful prompts in:
- `AGENT_WORKFLOW.md` for workflow patterns
- `ORCHESTRATION.md` for multi-agent coordination
- This file for prompt techniques

## Resources

- CoomerDL codebase: `/home/runner/work/CoomerDL/CoomerDL/`
- Task definitions: `TASKS.md`
- Roadmap: `ROADMAP.md`
- Performance analysis: `PERFORMANCE_ANALYSIS.md`
- Agent workflows: `AI_AGENT_WORKFLOW.md`
