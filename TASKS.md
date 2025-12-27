# CoomerDL Development Tasks

> **Purpose**: Actionable task definitions for AI coding agents and developers. Each task is self-contained with clear context, requirements, and acceptance criteria.

---

## 📝 Document Summary (AI Quick Start)

**What This Is**: Detailed breakdown of all development tasks with step-by-step implementation guidance

**How to Use**:
1. Find task ID from DEVELOPMENT_ROADMAP.md (e.g., T001, T004, T008)
2. Read full task definition here
3. Follow the implementation steps
4. Verify against acceptance criteria

**Task Categories**:
- **T001-T007**: Critical bug fixes (30 min - 1 hour each)
- **T008-T015**: Feature additions (2-8 hours each)
- **T016-T017**: Testing & code quality (4-12 hours)

**Key Information Per Task**:
- ✅ **File**: Exact file paths to modify
- ✅ **Problem**: What's broken or missing
- ✅ **Context**: Code snippets showing the issue
- ✅ **Requirements**: What must be implemented
- ✅ **Acceptance Criteria**: How to verify it works
- ✅ **Dependencies**: Other tasks that must be done first

**Most Common Tasks**:
- Bug fixes: Usually 1-10 line changes in a single file
- Refactoring: Pattern application across multiple files (e.g., threading.Event)
- Features: New classes/modules + UI integration + testing

**Testing Pattern**:
```bash
# 1. Test import
python -c "from downloader.module import Class; print('OK')"

# 2. Run application
python main.py

# 3. Test the specific feature
# (paste URL, click download, verify behavior)
```

---

## Quick Reference

| ID | Task | Priority | Complexity | Status |
|----|------|----------|------------|--------|
| T001 | Fix undefined `log_message` variable | Critical | Low | Open |
| T002 | Fix SimpCity missing `base_url` | Critical | Low | Open |
| T003 | Remove unused import in jpg5.py | Low | Trivial | Open |
| T004 | Standardize cancel mechanisms | Medium | Medium | Open |
| T005 | Fix database connection cleanup | Medium | Low | Open |
| T006 | Fix BunkrDownloader notification thread | Medium | Low | Open |
| T007 | Fix EromeDownloader folder_name scope | Medium | Low | Open |
| T008 | Add batch URL input support | High | Medium | Open |
| T009 | Create BaseDownloader abstract class | High | High | Open |
| T010 | Split ui.py into modules | High | High | Open |
| T011 | Add download queue manager | High | High | Open |
| T012 | Add proxy support | Medium | Medium | Open |
| T013 | Add bandwidth limiting | Medium | Medium | Open |
| T014 | Add filter by file size | Medium | Medium | Open |
| T015 | Add filter by date range | Medium | Medium | Open |
| T016 | Add unit test infrastructure | High | Medium | Open |
| T017 | Add type hints throughout codebase | Medium | Medium | Open |

---

## Critical Bug Fixes

### T001: Fix undefined `log_message` variable in Downloader.safe_request()

**File**: `downloader/downloader.py`

**Problem**: In the `safe_request()` method, `log_message` is referenced before being defined in the exception handler for status codes 429, 500-504.

**Context**:
```python
# Inside safe_request() exception handling
self.log(log_message)  # ERROR: log_message not defined at this point
```

**Requirements**:
1. Define `log_message` before it is used
2. Ensure appropriate error message for each status code type
3. Maintain existing retry logic

**Acceptance Criteria**:
- [ ] No `NameError` when handling 429/500-504 status codes
- [ ] Appropriate error messages logged for each status type
- [ ] Existing retry behavior preserved

**Estimated Effort**: 15 minutes

---

### T002: Fix SimpCity missing `base_url` in process_page()

**File**: `downloader/simpcity.py`

**Problem**: In `process_page()` method, `self.base_url` is referenced but never set, causing `AttributeError` when handling pagination.

**Context**:
```python
# Inside process_page()
self.process_page(self.base_url + next_page_url)  # ERROR: self.base_url never set
```

**Requirements**:
1. Extract base URL from initial URL in `download_images_from_simpcity()`
2. Store as instance variable `self.base_url`
3. Use for pagination URL construction

**Implementation Hint**:
```python
from urllib.parse import urlparse
parsed = urlparse(url)
self.base_url = f"{parsed.scheme}://{parsed.netloc}"
```

**Acceptance Criteria**:
- [ ] `self.base_url` is set before `process_page()` is called
- [ ] Pagination works correctly for multi-page threads
- [ ] No `AttributeError` during pagination

**Estimated Effort**: 20 minutes

---

### T003: Remove unused import in jpg5.py

**File**: `downloader/jpg5.py`

**Problem**: `from app import progress_manager` is imported but never used.

**Requirements**:
1. Remove the unused import line

**Acceptance Criteria**:
- [ ] Import removed
- [ ] File still functions correctly

**Estimated Effort**: 2 minutes

---

## Medium Priority Fixes

### T004: Standardize cancel mechanisms across downloaders

**Files**: All files in `downloader/` directory

**Problem**: Inconsistent cancellation patterns across downloaders:
- `Downloader` (`downloader.py`): Uses `threading.Event()` ✓
- `BunkrDownloader` (`bunkr.py`): Uses `self.cancel_requested = False`
- `EromeDownloader` (`erome.py`): Uses `self.cancel_requested = False`  
- `SimpCity` (`simpcity.py`): Uses `self.cancel_requested = False`
- `Jpg5Downloader` (`jpg5.py`): Uses `threading.Event()` ✓

**Requirements**:
1. Convert all boolean flag cancellation to `threading.Event()` pattern
2. Replace `self.cancel_requested = True` with `self.cancel_event.set()`
3. Replace `if self.cancel_requested:` with `if self.cancel_event.is_set():`

**Acceptance Criteria**:
- [ ] All downloaders use `threading.Event()` for cancellation
- [ ] Cancel functionality works correctly in all downloaders
- [ ] Thread-safe cancellation across all concurrent downloads

**Estimated Effort**: 1 hour

---

### T005: Fix database connection cleanup

**File**: `downloader/downloader.py`

**Problem**: Database connection opened in `init_db()` is never explicitly closed. No `__del__` method or context manager.

**Requirements**:
1. Add cleanup method for database connection
2. Call cleanup in `shutdown_executor()` method
3. Consider implementing context manager pattern

**Acceptance Criteria**:
- [ ] Database connection is properly closed on shutdown
- [ ] No resource leaks from SQLite connections
- [ ] Clean shutdown sequence

**Estimated Effort**: 30 minutes

---

### T006: Fix BunkrDownloader notification thread shutdown

**File**: `downloader/bunkr.py`

**Problem**: `start_notification_thread()` creates a daemon thread that polls `log_messages` list indefinitely with no clean shutdown mechanism.

**Requirements**:
1. Add shutdown flag that the notification thread checks
2. Set flag when download is cancelled or completed
3. Ensure thread exits cleanly

**Acceptance Criteria**:
- [ ] Notification thread stops when download completes/cancels
- [ ] No orphaned threads after download operations
- [ ] Clean resource cleanup

**Estimated Effort**: 30 minutes

---

### T007: Fix EromeDownloader folder_name scope issue

**File**: `downloader/erome.py`

**Problem**: In `process_album_page()`, `folder_name` may be undefined if `direct_download` is True.

**Context**:
```python
self.log(self.tr("Album download complete: {folder_name}", folder_name=folder_name))
# folder_name may be undefined if direct_download is True
```

**Requirements**:
1. Initialize `folder_name` with default value before conditional block
2. Ensure variable is always defined when logging

**Acceptance Criteria**:
- [ ] No `NameError` when `direct_download` is True
- [ ] Appropriate default folder name used in logs

**Estimated Effort**: 15 minutes

---

## Feature Tasks

### T008: Add batch URL input support

**Files**: `app/ui.py`

**Problem**: Currently only supports single URL input. Users must process URLs one at a time.

**Requirements**:
1. Replace single-line CTkEntry with multi-line CTkTextbox for URL input
2. Parse multiple URLs (one per line)
3. Add URL validation before adding to queue
4. Support drag-and-drop of text files containing URLs
5. Detect and warn about duplicate URLs

**Implementation Notes**:
- Use `url.strip()` for each line
- Skip empty lines
- Validate URL format before processing
- Show count of valid URLs detected

**UI Changes**:
```
Before: [Single URL Entry]
After:  [Multi-line Textarea]
        "Paste URLs (one per line) or drag & drop a text file"
        [URL count: X valid URLs detected]
```

**Acceptance Criteria**:
- [ ] Multi-line input accepts multiple URLs
- [ ] Empty lines are ignored
- [ ] Invalid URLs are flagged
- [ ] Duplicate URLs are detected
- [ ] Drag-and-drop works for .txt files

**Estimated Effort**: 3 hours

---

### T009: Create BaseDownloader abstract class

**Files**: New file `downloader/base.py`, modify all downloaders

**Problem**: Each downloader has different constructor signatures, methods, and patterns.

**Requirements**:
1. Create abstract base class `BaseDownloader` in new file
2. Define standard interface:
   - `__init__(download_folder, options, log_callback, progress_callback)`
   - `supports_url(url) -> bool`
   - `download(url) -> DownloadResult`
   - `request_cancel()`
   - `is_cancelled() -> bool`
3. Create data classes: `DownloadOptions`, `DownloadResult`, `MediaItem`
4. Migrate existing downloaders to inherit from base class

**Acceptance Criteria**:
- [ ] `BaseDownloader` abstract class created
- [ ] All downloaders inherit from `BaseDownloader`
- [ ] Common interface works for all site types
- [ ] Factory pattern allows URL-based downloader selection

**Estimated Effort**: 8 hours

**Dependencies**: T001, T002, T004, T005, T006, T007 should be completed first

---

### T010: Split ui.py into modules

**Files**: `app/ui.py` (1226 lines) → multiple files

**Problem**: Monolithic UI file mixing UI, logic, and state management.

**Target Structure**:
```
app/
├── main.py                    # Entry point (keep existing)
├── window/
│   ├── __init__.py
│   ├── main_window.py         # CTk root window setup
│   ├── menu_bar.py            # Custom menu bar
│   ├── input_panel.py         # URL input, folder selection
│   ├── options_panel.py       # Download options checkboxes
│   ├── action_panel.py        # Download/Cancel buttons
│   ├── log_panel.py           # Log textbox with controls
│   ├── progress_panel.py      # Progress bars
│   └── status_bar.py          # Footer with speed/ETA
```

**Requirements**:
1. Create `app/window/` directory structure
2. Extract each UI section into separate module
3. Maintain all existing functionality
4. Use events/callbacks for component communication
5. Update `main.py` to use new structure

**Acceptance Criteria**:
- [ ] All UI components in separate files
- [ ] `ui.py` no longer exists or is minimal wrapper
- [ ] All existing functionality preserved
- [ ] No import cycles
- [ ] Application runs correctly

**Estimated Effort**: 12 hours

---

### T011: Add download queue manager

**Files**: New `app/dialogs/queue_dialog.py`, modify `app/ui.py`

**Problem**: No way to manage multiple downloads - can't pause/resume/reorder.

**Requirements**:
1. Create `DownloadQueue` class to manage download items
2. Add queue manager dialog with:
   - List of queued URLs
   - Pause/Resume individual items
   - Cancel individual items
   - Reorder via drag-and-drop
   - Priority levels (high/normal/low)
3. Persist queue state to survive app restart
4. Add "Queue" button to main window with item count badge

**UI Design**:
```
┌─ Download Queue (5 items) ───────────────────────────┐
│ [⏸ Pause All] [▶ Resume All] [🗑 Clear Completed]   │
├──────────────────────────────────────────────────────┤
│ ⣿ 🎬 video_001.mp4    [████░░] 45%  [⏸][✗] ▲▼      │
│ ⣿ 🖼 image_002.jpg    Pending       [▶][✗] ▲▼      │
│ ⣿ 🎬 video_003.mp4    Pending       [▶][✗] ▲▼      │
└──────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Queue dialog shows all pending/active downloads
- [ ] Individual pause/resume/cancel works
- [ ] Drag-and-drop reordering works
- [ ] Queue persists across app restart
- [ ] Main window shows queue count

**Estimated Effort**: 10 hours

**Dependencies**: T008 (batch URL support)

---

### T012: Add proxy support

**Files**: `app/settings_window.py`, all downloaders

**Problem**: No way to configure proxy for network requests.

**Requirements**:
1. Add proxy settings to settings window:
   - Enable/Disable toggle
   - Proxy type dropdown (HTTP, SOCKS4, SOCKS5)
   - Proxy host/port inputs
   - Optional username/password
2. Pass proxy config to all downloaders
3. Configure `requests.Session` with proxy settings

**Implementation Notes**:
```python
# For requests library
proxies = {
    'http': 'http://user:pass@host:port',
    'https': 'http://user:pass@host:port'
}
session.proxies.update(proxies)
```

**Acceptance Criteria**:
- [ ] Proxy settings UI in settings window
- [ ] Settings persisted to config file
- [ ] All downloaders use proxy when configured
- [ ] Connection test button validates proxy

**Estimated Effort**: 4 hours

---

### T013: Add bandwidth limiting

**Files**: All downloaders

**Problem**: Downloads can saturate network connection with no throttling.

**Requirements**:
1. Add bandwidth limit setting (KB/s, 0 = unlimited)
2. Implement rate limiting in download loops
3. Use token bucket or leaky bucket algorithm

**Implementation Hint**:
```python
import time

class RateLimiter:
    def __init__(self, rate_limit_kbps):
        self.rate_limit = rate_limit_kbps * 1024  # Convert to bytes/sec
        self.last_check = time.time()
        self.bytes_sent = 0
    
    def throttle(self, chunk_size):
        if self.rate_limit <= 0:
            return
        self.bytes_sent += chunk_size
        elapsed = time.time() - self.last_check
        expected_time = self.bytes_sent / self.rate_limit
        if expected_time > elapsed:
            time.sleep(expected_time - elapsed)
```

**Acceptance Criteria**:
- [ ] Bandwidth limit setting in UI
- [ ] Downloads respect configured limit
- [ ] 0 means unlimited (default)
- [ ] Speed display shows throttled speed

**Estimated Effort**: 3 hours

---

### T014: Add filter by file size

**Files**: All downloaders, `app/settings_window.py`

**Problem**: No way to skip files above/below certain size.

**Requirements**:
1. Add min/max file size settings
2. Check Content-Length header before downloading
3. Skip files outside size range
4. Log skipped files with reason

**Acceptance Criteria**:
- [ ] Min/max size inputs in settings
- [ ] Files outside range are skipped
- [ ] Skipped files logged clearly
- [ ] Size check uses HEAD request when possible

**Estimated Effort**: 2 hours

---

### T015: Add filter by date range

**Files**: `downloader/downloader.py`

**Problem**: No way to download only posts from specific date range.

**Requirements**:
1. Add date range picker in UI (start date, end date)
2. Filter posts based on `published` field from API
3. Support "Last N days" shortcuts

**Acceptance Criteria**:
- [ ] Date range inputs in download options
- [ ] Only posts within range are downloaded
- [ ] "Last 7 days", "Last 30 days" shortcuts work
- [ ] Date range persists in settings

**Estimated Effort**: 3 hours

---

### T016: Add unit test infrastructure

**Files**: New `tests/` directory

**Problem**: No test coverage for any code.

**Requirements**:
1. Set up pytest infrastructure
2. Create test fixtures for common scenarios
3. Add unit tests for:
   - URL parsing and validation
   - File name sanitization
   - Download options validation
   - Configuration loading/saving
4. Add mock responses for HTTP testing

**Directory Structure**:
```
tests/
├── __init__.py
├── conftest.py              # Fixtures
├── test_url_parsing.py
├── test_file_naming.py
├── test_config.py
└── test_downloaders/
    ├── __init__.py
    ├── test_downloader.py
    ├── test_bunkr.py
    └── test_erome.py
```

**Acceptance Criteria**:
- [ ] pytest runs successfully
- [ ] Core utilities have test coverage
- [ ] Mock HTTP responses for downloaders
- [ ] CI can run tests

**Estimated Effort**: 6 hours

---

### T017: Add type hints throughout codebase

**Files**: All Python files

**Problem**: No type hints make code harder to understand and refactor.

**Requirements**:
1. Add type hints to all function signatures
2. Add type hints to class attributes
3. Use `typing` module for complex types
4. Run mypy to validate types

**Example**:
```python
# Before
def download_media(self, url, folder):
    ...

# After
def download_media(self, url: str, folder: str) -> DownloadResult:
    ...
```

**Acceptance Criteria**:
- [ ] All public functions have type hints
- [ ] All class attributes have type hints
- [ ] mypy passes without errors
- [ ] Type hints are accurate and useful

**Estimated Effort**: 8 hours

---

## Task Dependencies Graph

```
T001 ─┬─> T009 (BaseDownloader)
T002 ─┤
T004 ─┤
T005 ─┤
T006 ─┤
T007 ─┘

T008 (Batch URLs) ──> T011 (Queue Manager)

T010 (Split UI) ──> T011 (Queue Manager)

T009 (BaseDownloader) ─┬─> T012 (Proxy)
                       ├─> T013 (Bandwidth)
                       ├─> T014 (Size Filter)
                       └─> T015 (Date Filter)

T016 (Tests) can run in parallel with any task
T017 (Type Hints) best done after T009, T010
```

---

## Notes for AI Agents

### Before Starting Any Task:
1. Read the task requirements completely
2. Verify the file locations exist
3. Check for any changes since this document was created
4. Run existing tests to ensure baseline passes

### Code Style:
- Follow existing patterns in the codebase
- Use descriptive variable names
- Add docstrings to new functions/classes
- Keep changes minimal and focused

### Testing Changes:
1. Run the application: `python main.py`
2. Test the specific feature/fix
3. Verify no regressions in related areas

### When Task is Complete:
1. Ensure all acceptance criteria are met
2. Update task status in this file
3. Document any deviations from requirements
4. Note any follow-up work needed

---

*Last updated: December 2024*
