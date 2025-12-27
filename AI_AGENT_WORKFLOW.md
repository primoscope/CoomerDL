# AI Agent Optimized Workflow for CoomerDL

## Purpose

This document provides AI coding agents with an optimized workflow for working on CoomerDL tasks. It includes step-by-step procedures, common patterns, and best practices.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Workflow Patterns](#workflow-patterns)
3. [Code Navigation Guide](#code-navigation-guide)
4. [Common Operations](#common-operations)
5. [Testing Procedures](#testing-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Initial Setup (First Time Only)
```bash
cd /home/runner/work/CoomerDL/CoomerDL

# Verify structure
ls -la

# Check Python version
python --version  # Should be 3.8+

# Test imports
python -c "from app.ui import ImageDownloaderApp; print('OK')"
```

### Task Selection
1. Read ROADMAP_SUMMARY.md for task list
2. Choose based on priority: 🔴 CRITICAL → 🟠 HIGH → 🟡 MEDIUM → 🟢 LOW
3. Check dependencies before starting
4. Review POTENTIAL_ISSUES.md for known blockers

---

## Workflow Patterns

### Pattern 1: Critical Bug Fix (15-30 minutes)

**When:** BUG-001, BUG-002, BUG-003, BUG-004

**Steps:**
```
1. READ: Task description from ROADMAP.md
   └─ Note: File location, line number, problem description

2. LOCATE: Find exact code location
   └─ Use view() to read file
   └─ Use grep() to search for patterns

3. VERIFY: Understand current behavior
   └─ Read surrounding code
   └─ Identify variable scopes
   └─ Check for side effects

4. FIX: Apply minimal change (1-5 lines typically)
   └─ Use edit() tool
   └─ Follow existing code style
   └─ Add comment if complex

5. TEST: Verify fix works
   └─ Run: python main.py
   └─ Exercise the buggy codepath
   └─ Verify no new errors

6. REPORT: Commit and document
   └─ Use report_progress()
   └─ Include what was fixed
   └─ Note any side effects
```

**Example: BUG-001 (Fix undefined log_message)**
```bash
# Step 1: Read task
view /home/runner/work/CoomerDL/CoomerDL/ROADMAP.md --range 76-106

# Step 2: Locate code
view /home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py --range 190-220
grep "log_message" /home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py

# Step 3: Verify (read context)
# ... analyze code ...

# Step 4: Fix
edit /home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py \
  old_str="if status_code in (429, 500, 502, 503, 504):
        self.log(log_message)" \
  new_str="if status_code in (429, 500, 502, 503, 504):
        log_message = self.tr(\"Server error {status_code}, retrying...\").format(status_code=status_code)
        self.log(log_message)"

# Step 5: Test
python main.py
# ... test download with rate-limited URL ...

# Step 6: Report
report_progress(
  message="Fix BUG-001: Define log_message before use",
  checklist="- [x] Fix undefined log_message\n- [ ] Other bugs..."
)
```

---

### Pattern 2: Performance Optimization (1-3 hours)

**When:** PERF-001, PERF-002, etc.

**Steps:**
```
1. BENCHMARK: Measure current performance
   └─ Run test case and time it
   └─ Note memory usage if relevant
   └─ Document baseline

2. ANALYZE: Identify bottleneck
   └─ Read code carefully
   └─ Look for loops, I/O, database calls
   └─ Check algorithmic complexity

3. DESIGN: Plan optimization
   └─ Consider caching, parallelism, better algorithm
   └─ Ensure correctness is preserved
   └─ Estimate expected improvement

4. IMPLEMENT: Make changes
   └─ Apply optimization
   └─ Add comments explaining approach
   └─ Keep old code in comments for reference

5. BENCHMARK: Measure improvement
   └─ Run same test case
   └─ Compare to baseline
   └─ Document improvement %

6. VERIFY: Ensure correctness
   └─ Test edge cases
   └─ Check memory usage
   └─ Look for regressions

7. REPORT: Document results
   └─ Include before/after metrics
   └─ Note any tradeoffs
```

**Example: PERF-001 (Database Indexing)**
```python
# 1. Benchmark
import time
start = time.time()
from app.ui import ImageDownloaderApp
app = ImageDownloaderApp()
print(f"Startup: {time.time() - start:.2f}s")  # Baseline: ~5.3s

# 2. Analyze
# Problem: load_download_cache() does SELECT * FROM downloads
# Large tables (10k+ rows) load 50-100MB into memory

# 3. Design
# Solution: Add index on media_url, query on-demand instead of full cache

# 4. Implement
edit /home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py \
  old_str="def init_db(self):
		self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
		self.db_cursor = self.db_connection.cursor()
		self.db_cursor.execute(\"\"\"
			CREATE TABLE IF NOT EXISTS downloads (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				media_url TEXT UNIQUE,
				file_path TEXT,
				file_size INTEGER,
				user_id TEXT,
				post_id TEXT,
				downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		\"\"\")
		self.db_connection.commit()" \
  new_str="def init_db(self):
		self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
		self.db_cursor = self.db_connection.cursor()
		self.db_cursor.execute(\"\"\"
			CREATE TABLE IF NOT EXISTS downloads (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				media_url TEXT UNIQUE,
				file_path TEXT,
				file_size INTEGER,
				user_id TEXT,
				post_id TEXT,
				downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		\"\"\")
		# Add index for faster lookups
		self.db_cursor.execute(
			\"CREATE INDEX IF NOT EXISTS idx_media_url ON downloads(media_url)\"
		)
		self.db_connection.commit()"

# 5. Benchmark again
# Result: Startup ~1.2s (77% improvement)

# 6. Verify - test downloads still work

# 7. Report
report_progress(
  message="Add database index for media_url - 77% faster startup",
  checklist="..."
)
```

---

### Pattern 3: Feature Addition (2-8 hours)

**When:** FEATURE-001, FEATURE-002, etc.

**Steps:**
```
1. RESEARCH: Understand requirement
   └─ Read ROADMAP.md task description
   └─ Check SPECIFICATIONS.md for design details
   └─ Review POTENTIAL_ISSUES.md for gotchas
   └─ Check dependencies are complete

2. EXPLORE: Study existing code
   └─ Find similar existing features
   └─ Identify code patterns to follow
   └─ Note naming conventions
   └─ Check how settings are stored

3. DESIGN: Plan implementation
   └─ Break into subtasks
   └─ Identify files to create/modify
   └─ Design data structures
   └─ Plan testing approach

4. IMPLEMENT: Build feature incrementally
   └─ Start with data model
   └─ Add backend logic
   └─ Add UI components
   └─ Wire everything together

5. TEST: Verify functionality
   └─ Unit test individual components
   └─ Integration test full feature
   └─ Test edge cases
   └─ Check error handling

6. DOCUMENT: Update docs
   └─ Add docstrings
   └─ Update README if needed
   └─ Add usage examples

7. REPORT: Commit and demo
   └─ Report progress
   └─ Include screenshot/demo
   └─ Note any limitations
```

**Example: FEATURE-001 (Batch URL Input)**
```
1. Research
   - Read ROADMAP.md line 330-376
   - Goal: Replace single-line entry with multi-line textbox
   - Must handle multiple URLs (one per line)

2. Explore
   - Current: app/ui.py line ~320-340 has CTkEntry
   - Pattern: Other textboxes use CTkTextbox with get("1.0", "end-1c")

3. Design
   Subtasks:
   a. Replace CTkEntry with CTkTextbox
   b. Update get URL logic to parse multiple lines
   c. Add URL validation
   d. Update download logic to iterate URLs

4. Implement
   # a. Replace widget
   edit app/ui.py \
     old_str="self.entry_url = ctk.CTkEntry(...)" \
     new_str="self.entry_url = ctk.CTkTextbox(
         self.input_frame,
         height=80,
         wrap=\"none\"
     )"
   
   # b. Parse URLs
   def get_urls(self):
       text = self.entry_url.get("1.0", "end-1c")
       urls = [line.strip() for line in text.split('\n') if line.strip()]
       return urls
   
   # c. Validate
   def validate_urls(self, urls):
       valid = []
       for url in urls:
           if urlparse(url).scheme in ('http', 'https'):
               valid.append(url)
           else:
               self.log(f"Invalid URL: {url}")
       return valid
   
   # d. Update download
   urls = self.validate_urls(self.get_urls())
   for url in urls:
       self.start_download(url)

5. Test
   - Paste 5 URLs, verify all downloaded
   - Test with empty lines
   - Test with invalid URLs
   - Test with single URL (backward compat)

6. Document
   - Add docstring to get_urls()
   - Add comment explaining URL parsing

7. Report with screenshot
```

---

### Pattern 4: Refactoring (4-12 hours)

**When:** REFACTOR-001, ARCH-001, etc.

**Steps:**
```
1. ASSESS: Understand current state
   └─ Read entire module/file
   └─ Map out dependencies
   └─ Identify all usage locations
   └─ Note any hacks or workarounds

2. DESIGN: Plan new structure
   └─ Draw module boundaries
   └─ Define interfaces
   └─ Plan migration path
   └─ Identify breaking changes

3. TEST: Establish baseline
   └─ Run all existing tests
   └─ Document current behavior
   └─ Note any existing bugs

4. REFACTOR: Transform incrementally
   └─ Extract one component at a time
   └─ Run tests after each extraction
   └─ Update imports immediately
   └─ Keep git history clean

5. VERIFY: Ensure equivalence
   └─ Run all tests
   └─ Manually test UI flows
   └─ Check performance unchanged
   └─ Review git diff

6. CLEANUP: Remove old code
   └─ Delete dead code
   └─ Update documentation
   └─ Fix deprecation warnings

7. REPORT: Document changes
   └─ List moved functions/classes
   └─ Note any behavior changes
   └─ Update architecture docs
```

**Example: REFACTOR-001 (Standardize Cancellation)**
```
1. Assess
   - downloader.py: Uses threading.Event() ✓
   - bunkr.py: Uses boolean flag ✗
   - erome.py: Uses boolean flag ✗
   - simpcity.py: Uses boolean flag ✗
   - jpg5.py: Uses threading.Event() ✓

2. Design
   Replace all: self.cancel_requested = False
   With: self.cancel_event = threading.Event()
   
   Replace: if self.cancel_requested:
   With: if self.cancel_event.is_set():
   
   Replace: self.cancel_requested = True
   With: self.cancel_event.set()

3. Test baseline
   python main.py
   # Start download, click cancel, verify it stops

4. Refactor (one file at a time)
   # bunkr.py
   edit downloader/bunkr.py \
     old_str="self.cancel_requested = False" \
     new_str="self.cancel_event = threading.Event()"
   
   # Find all usages
   grep "cancel_requested" downloader/bunkr.py
   
   # Replace each occurrence
   # ... (multiple edits) ...
   
   # Test bunkr
   python main.py
   # Test bunkr download + cancel
   
   # Repeat for erome.py
   # Repeat for simpcity.py

5. Verify
   # Test all downloaders with cancellation
   # Check thread safety with concurrent downloads

6. Cleanup
   # Remove any old commented code
   # Ensure consistent naming

7. Report
   report_progress(
     message="Standardize cancellation to threading.Event() across all downloaders",
     checklist="- [x] bunkr.py\n- [x] erome.py\n- [x] simpcity.py"
   )
```

---

## Code Navigation Guide

### File Organization
```
CoomerDL/
├── app/
│   ├── ui.py              # Main window (1226 lines) - REFACTOR TARGET
│   ├── settings_window.py # Settings dialog (906 lines)
│   ├── progress_manager.py# Progress tracking (192 lines)
│   ├── about_window.py    # About dialog (185 lines)
│   └── donors.py          # Donors list (222 lines)
├── downloader/
│   ├── downloader.py      # Main downloader (725 lines) - coomer/kemono
│   ├── bunkr.py           # Bunkr support (360 lines)
│   ├── erome.py           # Erome support (288 lines)
│   ├── simpcity.py        # SimpCity support (140 lines)
│   └── jpg5.py            # Jpg5 support (110 lines)
├── resources/config/      # Settings, DB, cookies
├── main.py                # Entry point (7 lines)
├── ROADMAP.md             # Detailed task descriptions
├── TASKS.md               # Task definitions
├── SPECIFICATIONS.md      # Design specs for new features
└── POTENTIAL_ISSUES.md    # Known problems
```

### Key Functions by Purpose

**Download Initiation:**
- `app/ui.py:start_download()` - Route URL to correct downloader
- `downloader/downloader.py:download_media()` - Main download orchestrator

**Progress Tracking:**
- `app/progress_manager.py:ProgressManager` - Global progress bar
- `downloader/downloader.py:update_progress_callback` - Per-file progress

**Settings:**
- `app/settings_window.py:load_settings()` - Load from JSON
- `app/settings_window.py:save_settings()` - Persist to JSON

**Database:**
- `downloader/downloader.py:init_db()` - SQLite schema creation
- `downloader/downloader.py:load_download_cache()` - Load existing downloads

**Network:**
- `downloader/downloader.py:safe_request()` - Rate-limited HTTP GET
- `downloader/downloader.py:_find_valid_subdomain()` - Subdomain probing

---

## Common Operations

### Reading Files
```python
# View full file
view("/home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py")

# View specific lines
view("/home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py", view_range=[100, 150])

# Search for pattern
grep(pattern="def download", path="/home/runner/work/CoomerDL/CoomerDL/downloader")
```

### Editing Files
```python
# Single replacement
edit(
    path="/home/runner/work/CoomerDL/CoomerDL/downloader/downloader.py",
    old_str="self.max_retries = max_retries",
    new_str="self.max_retries = max(1, max_retries)  # Ensure at least 1 retry"
)

# Multiple edits (sequential)
edit(path="file.py", old_str="old1", new_str="new1")
edit(path="file.py", old_str="old2", new_str="new2")
```

### Running Code
```bash
# Run application
python main.py

# Test import
python -c "from downloader.downloader import Downloader; print('OK')"

# Check syntax
python -m py_compile downloader/downloader.py

# Run with specific settings
python main.py --log-level DEBUG
```

### Testing Changes
```bash
# Manual test workflow
python main.py
# 1. Enter test URL
# 2. Click download
# 3. Observe logs
# 4. Verify files downloaded
# 5. Test cancel button
# 6. Check for errors
```

---

## Testing Procedures

### Unit Test Pattern (When TEST-001 is complete)
```python
# tests/test_downloader.py
import pytest
from downloader.downloader import Downloader

def test_file_naming():
    downloader = Downloader("/tmp", max_workers=1)
    filename = downloader.get_filename(
        "https://example.com/image.jpg",
        post_id="123"
    )
    assert filename.endswith(".jpg")
    assert "123" in filename

def test_media_folder_structure():
    downloader = Downloader("/tmp", folder_structure="post_number")
    folder = downloader.get_media_folder(".jpg", "user1", "post123")
    assert "user1" in folder
    assert "post_123" in folder
```

### Integration Test Pattern
```python
# tests/test_integration.py
def test_full_download_workflow():
    app = ImageDownloaderApp()
    # Enter URL
    app.entry_url.insert("1.0", "https://test.url")
    # Click download
    app.start_download()
    # Wait for completion
    # Assert files exist
```

### Manual Testing Checklist
```
Download Functionality:
[ ] Single URL download works
[ ] Multiple URLs download (when FEATURE-001 complete)
[ ] Cancel during download works
[ ] Resume after cancel works
[ ] Progress bar updates smoothly
[ ] Speed/ETA displayed correctly
[ ] Errors logged clearly

Settings:
[ ] Theme change applies immediately
[ ] Language change applies immediately
[ ] Max workers setting respected
[ ] Folder structure setting applied
[ ] Settings persist after restart

Edge Cases:
[ ] Empty URL shows error
[ ] Invalid URL shows error
[ ] Network error handled gracefully
[ ] Disk full handled gracefully
[ ] Duplicate download skipped
```

---

## Troubleshooting

### Common Errors

**Import Error: ModuleNotFoundError**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Run from correct directory
cd /home/runner/work/CoomerDL/CoomerDL
python main.py
```

**SQLite Error: database is locked**
```python
# Cause: Multiple threads accessing without lock
# Fix: Always use self.db_lock:
with self.db_lock:
    self.db_cursor.execute(...)
```

**Threading Error: Event already set**
```python
# Cause: Reusing Event without clearing
# Fix: Create new Event or call .clear():
self.cancel_event.clear()
```

**UI Freeze**
```python
# Cause: Long operation on main thread
# Fix: Use threading:
def long_operation():
    # ... do work ...
threading.Thread(target=long_operation, daemon=True).start()
```

### Debugging Tips

**Enable Verbose Logging**
```python
# In downloader __init__:
import logging
logging.basicConfig(level=logging.DEBUG)
self.logger = logging.getLogger(__name__)
```

**Trace Execution**
```python
# Add at suspicious locations:
import traceback
traceback.print_stack()
```

**Profile Performance**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

**Memory Profiling**
```python
import tracemalloc

tracemalloc.start()
# ... code to profile ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

---

## Best Practices

### Code Style
- Follow PEP 8
- Use 4 spaces (not tabs)
- Max line length: 100-120 characters
- Docstrings for public functions
- Type hints where helpful

### Git Commits
```bash
# Good commit messages:
"Fix BUG-001: Define log_message before use in safe_request()"
"Add database index on media_url for faster lookups"
"Refactor: Extract menu bar into separate module"

# Bad commit messages:
"Fix bug"
"Update code"
"Changes"
```

### Performance
- Profile before optimizing
- Measure before and after
- Document improvements in commit
- Check for regressions

### Safety
- Always backup database before schema changes
- Test cancellation for new features
- Check thread safety
- Handle errors gracefully
- Clean up resources (files, connections, threads)

---

## Quick Reference

### Most Common Tasks
```bash
# Fix undefined variable
1. grep "variable_name" file.py
2. Find usage location
3. Add initialization before use

# Add feature flag
1. Add to settings.json default values
2. Load in settings_window.py
3. Use in downloader: if self.feature_enabled:

# Speed up slow function
1. Profile with cProfile
2. Identify bottleneck (usually I/O or algorithm)
3. Add caching, parallelize, or optimize algorithm
4. Measure improvement

# Refactor large file
1. Create new directory structure
2. Extract one class/function at a time
3. Update imports after each move
4. Test after each move
5. Delete old file when done
```

### Useful Commands
```bash
# Find all TODO comments
grep -r "TODO" --include="*.py" .

# Count lines by file
wc -l **/*.py | sort -rn

# Find all print statements (should use logging)
grep -r "print(" --include="*.py" .

# Check for bare exceptions
grep -r "except:" --include="*.py" .

# Find duplicate code
# (use external tool like PMD-CPD)
```

---

## Conclusion

This workflow document provides AI agents with:
- ✅ Step-by-step patterns for common tasks
- ✅ Code navigation guidance
- ✅ Testing procedures
- ✅ Troubleshooting tips
- ✅ Best practices

**Remember:**
1. Start with ROADMAP_SUMMARY.md for task selection
2. Use PERFORMANCE_ANALYSIS.md for optimization guidance
3. Check POTENTIAL_ISSUES.md before major changes
4. Report progress frequently
5. Test thoroughly before marking complete

**Success Criteria:**
- Code works correctly
- Tests pass (when available)
- Performance improved (for optimization tasks)
- No regressions introduced
- Clean git history

---

*Last Updated: December 2024*  
*Version: 1.0*  
*For: AI Coding Agents*
