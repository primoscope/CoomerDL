# CoomerDL Roadmap Summary

---

## 🎯 Quick Overview (AI Agent Fast Track)

**Purpose**: Prioritized task list - pick tasks by priority and start working immediately

**At a Glance**:
- 🔴 **2 Critical bugs** → 35 minutes (fix these first!)
- 🟠 **7 High priority** → 53 hours (important features)
- 🟡 **11 Medium priority** → 34 hours (nice improvements)
- 🟢 **3 Low priority** → 6 hours (polish)

**Recommended Approach**:
1. Start with 🔴 CRITICAL bugs (BUG-001, BUG-002)
2. Move to 🟠 HIGH features (BaseDownloader, UI split, queue manager)
3. Then 🟡 MEDIUM improvements (filters, proxy, bandwidth)
4. Finally 🟢 LOW enhancements (polish)

**Each Task Includes**:
- ⏱️ Time estimate
- 📁 Exact file location
- 🔧 Problem description
- ✅ Fix/implementation details
- 🧪 Test instructions

**Jump to**:
- [Critical Tasks](#priority-1--critical-fix-immediately) - Start here
- [High Priority](#priority-2--high-do-soon) - Next focus
- [Quick Wins](#quick-wins-under-1-hour) - Easy points
- [Dependency Graph](#task-dependencies) - What requires what

---

## Quick Reference for AI Agents

This document provides a prioritized summary of all tasks from ROADMAP.md organized by priority and actionability.

---

## Task Overview

| Priority | Count | Category | Estimated Time |
|----------|-------|----------|----------------|
| 🔴 CRITICAL | 2 | Bug Fixes | 35 minutes |
| 🟠 HIGH | 7 | Features + Refactoring | 53 hours |
| 🟡 MEDIUM | 11 | Improvements | 34 hours |
| 🟢 LOW | 3 | Enhancements | 6 hours |
| **TOTAL** | **23** | **All** | **~93 hours** |

---

## Priority 1: 🔴 CRITICAL (Fix Immediately)

### BUG-001: Fix undefined `log_message` variable ⏱️ 15 min
- **File:** `downloader/downloader.py`
- **Location:** `safe_request()` method, line ~194
- **Problem:** NameError when server returns 429/500-504 status codes
- **Fix:**
  ```python
  # Line 194, BEFORE self.log(log_message):
  log_message = self.tr("Server error {status_code}, retrying...").format(
      status_code=status_code
  )
  self.log(log_message)
  ```
- **Test:** Try downloading from rate-limited URL
- **Impact:** 🔥 App crashes on server errors

---

### BUG-002: Fix SimpCity missing `base_url` ⏱️ 20 min
- **File:** `downloader/simpcity.py`
- **Location:** `download_images_from_simpcity()` method
- **Problem:** AttributeError on multi-page threads (pagination fails)
- **Fix:**
  ```python
  # Add before process_page() is called:
  from urllib.parse import urlparse
  parsed = urlparse(url)
  self.base_url = f"{parsed.scheme}://{parsed.netloc}"
  ```
- **Test:** Download multi-page SimpCity thread
- **Impact:** 🔥 Pagination completely broken

---

## Priority 2: 🟠 HIGH (Do Next)

### REFACTOR-001: Standardize cancel mechanisms ⏱️ 2 hours
- **Files:** `bunkr.py`, `erome.py`, `simpcity.py`
- **Problem:** Thread-unsafe boolean flags for cancellation
- **Fix:** Replace `self.cancel_requested = False` with `threading.Event()`
- **Impact:** Race conditions during concurrent cancellations

---

### FEATURE-001: Add batch URL input ⏱️ 3 hours
- **File:** `app/ui.py`
- **Problem:** Must process URLs one at a time
- **Changes:**
  1. Replace CTkEntry with CTkTextbox (multi-line)
  2. Parse URLs line-by-line
  3. Skip empty lines, validate URLs
- **Impact:** Major UX improvement for bulk downloads

---

### FEATURE-002: Create BaseDownloader class ⏱️ 8 hours
- **Files:** New `downloader/base.py`, all downloaders
- **Problem:** Inconsistent interfaces across downloaders
- **Requirements:**
  - Abstract base with `supports_url()`, `download()`, `request_cancel()`
  - Data classes: `DownloadOptions`, `DownloadResult`, `MediaItem`
  - Factory pattern for URL-based selection
- **Dependencies:** BUG-001, BUG-002, REFACTOR-001 must be done first
- **Impact:** Foundation for all future downloader features

---

### FEATURE-003: Add download queue manager ⏱️ 10 hours
- **Files:** New `app/dialogs/queue_dialog.py`, modify `app/ui.py`
- **Problem:** No pause/resume/reorder capability
- **Requirements:**
  - Queue window with item list
  - Per-item pause/resume/cancel controls
  - Drag-and-drop reordering
  - Persist queue across restarts
- **Dependencies:** FEATURE-001 (batch URLs)
- **Impact:** Professional-grade download management

---

### ARCH-001: Split ui.py into modules ⏱️ 12 hours
- **File:** `app/ui.py` (1,226 lines) → `app/window/*.py`
- **Problem:** God class anti-pattern
- **Target Structure:**
  ```
  app/window/
  ├── main_window.py    # Root window
  ├── menu_bar.py       # Menu system
  ├── input_panel.py    # URL input
  ├── options_panel.py  # Checkboxes
  ├── log_panel.py      # Log display
  └── status_bar.py     # Footer
  ```
- **Impact:** Maintainability, testability, extensibility

---

### TEST-001: Add unit test infrastructure ⏱️ 6 hours
- **Files:** New `tests/` directory
- **Requirements:**
  - pytest setup with fixtures
  - Tests for URL parsing, file naming, config
  - Mock HTTP responses for downloaders
- **Impact:** Prevent regressions, enable refactoring

---

## Priority 3: 🟡 MEDIUM (Nice to Have)

### BUG-003: Remove unused import ⏱️ 2 min
- **File:** `downloader/jpg5.py`
- **Fix:** Delete `from app import progress_manager`
- **Impact:** Code cleanliness

---

### BUG-004: Fix EromeDownloader folder_name scope ⏱️ 15 min
- **File:** `downloader/erome.py`, `process_album_page()`
- **Fix:** Initialize `folder_name = "direct_download"` before conditional
- **Impact:** NameError on direct downloads

---

### REFACTOR-002: Fix database connection cleanup ⏱️ 30 min
- **File:** `downloader/downloader.py`
- **Fix:**
  ```python
  def shutdown_executor(self):
      # ... existing code ...
      if hasattr(self, 'db_connection') and self.db_connection:
          self.db_connection.close()
          self.db_connection = None
  ```
- **Impact:** Resource leak, clean shutdown

---

### REFACTOR-003: Fix BunkrDownloader notification thread ⏱️ 30 min
- **File:** `downloader/bunkr.py`
- **Fix:** Add shutdown Event and check in loop
- **Impact:** Orphaned threads

---

### FEATURE-004: Add proxy support ⏱️ 4 hours
- **Files:** `app/settings_window.py`, all downloaders
- **Requirements:**
  - Settings UI for proxy config (type, host, port, auth)
  - Apply to `requests.Session`
- **Impact:** Users behind firewalls/proxies

---

### FEATURE-005: Add bandwidth limiting ⏱️ 3 hours
- **Files:** All downloaders
- **Requirements:**
  - Rate limiter class with token bucket algorithm
  - Settings UI for KB/s limit
- **Impact:** Prevent network saturation

---

### FEATURE-006: Add file size filter ⏱️ 2 hours
- **Files:** All downloaders, `app/settings_window.py`
- **Requirements:**
  - Min/max size inputs
  - Check Content-Length before download
- **Impact:** Skip unwanted large/small files

---

### FEATURE-007: Add date range filter ⏱️ 3 hours
- **File:** `downloader/downloader.py`
- **Requirements:**
  - Date picker in UI
  - Filter posts by `published` field
  - "Last N days" shortcuts
- **Impact:** Download only recent content

---

### TEST-002: Add type hints ⏱️ 8 hours
- **Files:** All Python files
- **Requirements:**
  - Type hints for all function signatures
  - Type hints for class attributes
  - mypy validation passing
- **Dependencies:** Best done after FEATURE-002, ARCH-001
- **Impact:** Better IDE support, catch bugs early

---

## Optimized Workflow for AI Agents

### Phase 1: Foundation (Week 1)
**Goal:** Fix critical bugs and add performance wins

```
Day 1: Critical Bugs
├─ 09:00-09:15  BUG-001: Fix log_message (15 min)
├─ 09:15-09:35  BUG-002: Fix base_url (20 min)
├─ 09:35-10:05  REFACTOR-002: Database cleanup (30 min)
└─ 10:05-10:15  BUG-003: Remove unused import (10 min)
                Total: 75 minutes

Day 2: Performance Optimizations
├─ 09:00-10:00  PERF-001: Database indexing (1 hour)
├─ 10:00-11:30  PERF-003: Progress throttling (1.5 hours)
└─ 11:30-12:00  PERF-004: Connection pooling (30 min)
                Total: 3 hours

Day 3: Thread Safety
├─ 09:00-10:00  BUG-004: folder_name scope (1 hour)
├─ 10:00-12:00  REFACTOR-001: Standardize cancellation (2 hours)
└─ 12:00-12:30  REFACTOR-003: BunkrDownloader thread (30 min)
                Total: 3.5 hours
```

**Deliverables:**
- ✅ Zero critical bugs
- ✅ 50% faster startup
- ✅ Smoother UI
- ✅ Thread-safe cancellation

---

### Phase 2: Architecture (Week 2-3)
**Goal:** Create clean, testable foundation

```
Week 2: BaseDownloader + Tests
├─ Mon-Tue:  FEATURE-002: BaseDownloader class (8 hours)
├─ Wed:      TEST-001: Unit test infrastructure (6 hours)
├─ Thu:      Migrate one downloader to BaseDownloader (4 hours)
└─ Fri:      Testing and bug fixes (4 hours)
             Total: 22 hours

Week 3: UI Refactoring
├─ Mon-Wed:  ARCH-001: Split ui.py (12 hours)
├─ Thu:      FEATURE-001: Batch URL input (3 hours)
└─ Fri:      Integration testing (3 hours)
             Total: 18 hours
```

**Deliverables:**
- ✅ Standardized downloader interface
- ✅ Test coverage >30%
- ✅ Modular UI architecture
- ✅ Batch URL support

---

### Phase 3: Features (Week 4-5)
**Goal:** Add user-requested features

```
Week 4: Download Management
├─ Mon-Wed:  FEATURE-003: Queue manager (10 hours)
├─ Thu:      FEATURE-004: Proxy support (4 hours)
└─ Fri:      FEATURE-005: Bandwidth limiting (3 hours)
             Total: 17 hours

Week 5: Filters & Polish
├─ Mon:      FEATURE-006: File size filter (2 hours)
├─ Tue:      FEATURE-007: Date range filter (3 hours)
├─ Wed-Fri:  TEST-002: Add type hints (8 hours)
             Total: 13 hours
```

**Deliverables:**
- ✅ Professional download queue
- ✅ Network configuration options
- ✅ Advanced filtering
- ✅ Type-safe codebase

---

## Agent Execution Patterns

### Pattern 1: Quick Bug Fix (15-30 min)
```
1. Read task description from ROADMAP.md
2. Locate file and problem line
3. Apply minimal fix
4. Test with provided command
5. Report progress
```

### Pattern 2: Feature Addition (2-8 hours)
```
1. Check SPECIFICATIONS.md for design details
2. Check POTENTIAL_ISSUES.md for blockers
3. Implement in isolated branch
4. Add unit tests
5. Integration test
6. Report progress with examples
```

### Pattern 3: Refactoring (8-12 hours)
```
1. Create target structure
2. Extract one module at a time
3. Run tests after each extraction
4. Update imports
5. Verify all functionality preserved
6. Report progress incrementally
```

---

## Success Metrics

### After Phase 1 (Week 1)
- [ ] Zero `NameError` or `AttributeError` crashes
- [ ] Startup time <2 seconds (from ~5s)
- [ ] UI stays responsive during downloads
- [ ] Cancellation works 100% of the time

### After Phase 2 (Week 3)
- [ ] All downloaders use BaseDownloader
- [ ] Test coverage >30%
- [ ] ui.py <300 lines (from 1,226)
- [ ] Can paste 10 URLs at once

### After Phase 3 (Week 5)
- [ ] Queue manager fully functional
- [ ] Proxy configuration working
- [ ] Type hints throughout codebase
- [ ] mypy passing without errors

---

## Risk Mitigation

### High Risk Areas
1. **Database migration** - Always backup before schema changes
2. **UI refactoring** - Test every screen after each module split
3. **Threading changes** - Stress test with 100+ concurrent downloads

### Rollback Strategy
- Git branches for each major feature
- Feature flags for experimental code
- Database schema versioning

---

## Dependencies Graph

```
Critical Path:
BUG-001, BUG-002 ──> REFACTOR-001 ──> FEATURE-002 (BaseDownloader)
                                            │
                                            ├──> FEATURE-004 (Proxy)
                                            ├──> FEATURE-005 (Bandwidth)
                                            ├──> FEATURE-006 (Size Filter)
                                            └──> FEATURE-007 (Date Filter)

Parallel Paths:
FEATURE-001 (Batch URLs) ──> FEATURE-003 (Queue Manager)

ARCH-001 (Split UI) ──> FEATURE-003 (Queue Manager)
                    └──> Better maintainability for future features

Independent:
TEST-001 (can run anytime)
TEST-002 (best after FEATURE-002 + ARCH-001)
```

---

## Quick Task Finder

**Want to fix crashes?** → BUG-001, BUG-002  
**Want faster performance?** → PERF-001, PERF-002, PERF-003  
**Want better UX?** → FEATURE-001, FEATURE-003  
**Want cleaner code?** → ARCH-001, FEATURE-002  
**Want new features?** → FEATURE-004, FEATURE-005, FEATURE-006  
**Want better testing?** → TEST-001, TEST-002  

---

## Agent Instructions

### For Bug Fixes (BUG-*)
1. Locate exact line number using grep/view
2. Apply minimal fix (usually 1-5 lines)
3. Run application and test scenario
4. Report success with screenshot

### For Refactoring (REFACTOR-*)
1. Read current implementation
2. Identify all usage locations
3. Apply changes systematically
4. Run existing tests
5. Report before/after comparison

### For Features (FEATURE-*)
1. Check SPECIFICATIONS.md for design
2. Check dependencies are complete
3. Implement with tests
4. Update documentation
5. Report with demo/screenshot

### For Architecture (ARCH-*)
1. Create new structure first
2. Move code incrementally
3. Test after each move
4. Update all imports
5. Report file tree before/after

---

## Final Notes

- **Always start with critical bugs** - they block everything else
- **Test early and often** - don't wait until end
- **Report progress frequently** - after each completed task
- **Use existing patterns** - consistency matters
- **Ask when unsure** - don't guess on breaking changes

**Total Estimated Time:** 93 hours (~2.3 weeks at 40 hrs/week)  
**Minimum Viable Improvement:** Phase 1 only (1 week, fixes crashes + performance)  
**Recommended Path:** All 3 phases for complete modernization

---

*Last Updated: December 2024*  
*Version: 1.0*  
*Based on: DEVELOPMENT_ROADMAP.md, TASKS.md, SPECIFICATIONS.md*
