# CoomerDL Improvement Roadmap

---

## 🎯 Executive Summary (AI Agent Quick Reference)

**Purpose**: Complete guide for AI agents working on CoomerDL improvements

**Quick Stats**:
- **Total Tasks**: 71 (17 bugs, 24 features, 15 refactors, 15 tests/docs)
- **Critical Bugs**: 4 (BUG-001 to BUG-004)
- **High Priority**: 12 tasks
- **Code Size**: ~6,000 lines across 20+ main files

**Recent Major Features Completed** ✅:
1. **Universal Mode (yt-dlp)**: 1000+ site support via `downloader/ytdlp_adapter.py`
2. **Gallery Engine (gallery-dl)**: Image gallery support via `downloader/gallery.py`
3. **Job Queue System**: Persistent history, events, crash recovery via `downloader/queue.py`, `downloader/history.py`, `downloader/models.py`
4. **Press & Forget Hardening**: Retry policies, rate limiting via `downloader/policies.py`, `downloader/ratelimiter.py`
5. **Smart Factory Routing**: 4-tier fallback (native → gallery → yt-dlp → generic) via `downloader/factory.py`
6. **Test Infrastructure**: 241 tests, contracts documentation via `tests/`

**Common Task Types**:
1. **Bug Fixes** (15-30 min): Single-line to small fixes, test with `python main.py`
2. **Refactoring** (1-3 hours): Standardize patterns, improve code quality
3. **Features** (2-8 hours): New UI/functionality, requires design + testing
4. **Architecture** (4-12 hours): Large structural changes, multi-file coordination

**Key Patterns**:
- Threading: Use `threading.Event()` for cancellation (not boolean flags)
- Database: Use indexed queries with `db_lock` (no full table scans)
- Progress: Throttle callbacks to 0.1s intervals (10 FPS max)
- Sessions: Reuse `requests.Session()` with connection pooling
- Factory: Use `@classmethod can_handle(url)` for lightweight URL routing
- Events: Backend emits events (JOB_ADDED, JOB_DONE, etc.), UI subscribes

**Priority Guide**:
- 🔴 CRITICAL → Fix immediately (crashes, data loss)
- 🟠 HIGH → Fix soon (important features, major bugs)
- 🟡 MEDIUM → Nice to have (improvements, minor bugs)
- 🟢 LOW → Optional (polish, edge cases)
- ✅ DONE → Completed (for reference)

**Workflow**:
1. Choose task from [Task Index](#task-index)
2. Read full task details (FILE, PROBLEM, SOLUTION, DONE WHEN)
3. Check dependencies (some tasks require others first)
4. Follow pattern in `AI_AGENT_WORKFLOW.md`
5. Test with `python main.py` and verify acceptance criteria
6. Run `pytest tests/` to ensure no regressions

---

> **For AI Coding Agents**: This document is optimized for AI agents. Start with [Quick Start for Agents](#quick-start-for-agents), then use [Task Index](#task-index) to find specific work items. Each task has clear acceptance criteria and file locations.

> **For Humans**: This document outlines proposed improvements for CoomerDL. See [TASKS.md](TASKS.md) for detailed task breakdowns and [SPECIFICATIONS.md](SPECIFICATIONS.md) for implementation details.

---

## Quick Start for Agents

### How to Use This Document

1. **Find a task**: Use the [Task Index](#task-index) table below
2. **Read the task**: Each task has `FILE:`, `PROBLEM:`, `SOLUTION:`, and `DONE WHEN:` sections
3. **Check dependencies**: Some tasks require others to be completed first
4. **Implement**: Make minimal changes to fix the specific issue
5. **Verify**: Run the acceptance criteria checks

### Priority Levels
- 🔴 **CRITICAL**: Bugs that cause crashes or data loss - fix first
- 🟠 **HIGH**: Important features or significant bugs
- 🟡 **MEDIUM**: Improvements and minor bugs
- 🟢 **LOW**: Nice-to-have enhancements

### File Structure Reference
```
CoomerDL/
├── app/
│   ├── ui.py                 # Main UI (1226 lines) - needs refactoring
│   ├── settings_window.py    # Settings dialog with Universal (yt-dlp) tab
│   ├── progress_manager.py   # Progress tracking (192 lines)
│   ├── about_window.py       # About dialog (185 lines)
│   ├── donors.py             # Donors modal (222 lines)
│   └── utils/
│       ├── ffmpeg_check.py   # FFmpeg availability detection
│       └── gallerydl_check.py # gallery-dl availability detection
├── downloader/
│   ├── base.py               # ✅ BaseDownloader abstract class
│   ├── factory.py            # ✅ Smart URL routing with can_handle()
│   ├── ytdlp_adapter.py      # ✅ YtDlpDownloader (1000+ sites)
│   ├── gallery.py            # ✅ GalleryDownloader (gallery-dl)
│   ├── queue.py              # ✅ DownloadQueueManager
│   ├── history.py            # ✅ SQLite job/event persistence
│   ├── models.py             # ✅ JobStatus, ItemStatus, DownloadEvent
│   ├── policies.py           # ✅ RetryPolicy, DomainPolicy
│   ├── ratelimiter.py        # ✅ Per-domain rate limiting
│   ├── downloader.py         # Core downloader for coomer/kemono (725 lines)
│   ├── bunkr.py              # Bunkr downloader (360 lines)
│   ├── erome.py              # Erome downloader (288 lines)
│   ├── simpcity.py           # SimpCity downloader (138 lines)
│   ├── reddit.py             # Reddit downloader
│   ├── generic.py            # Generic HTML scraper (fallback)
│   └── jpg5.py               # Jpg5 downloader (112 lines)
├── tests/
│   ├── CONTRACTS.md          # ✅ System behavior contracts
│   ├── conftest.py           # Test fixtures
│   ├── test_contracts.py     # Contract verification tests
│   ├── test_user_journeys.py # User journey tests
│   ├── test_job_queue.py     # Job queue system tests
│   ├── test_gallery_policies.py # Gallery/policies tests
│   ├── test_factory.py       # Factory routing tests
│   └── ...                   # 241 total tests
├── resources/
│   └── config/               # JSON configs, SQLite DB, cookies
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies including yt-dlp, gallery-dl
├── TASKS.md                  # Detailed task definitions
├── SPECIFICATIONS.md         # New class/function specifications
└── POTENTIAL_ISSUES.md       # Known issues and blockers
```

---

## Task Index

| ID | Priority | Task | File(s) | Complexity |
|----|----------|------|---------|------------|
| BUG-001 | 🔴 | Fix undefined `log_message` variable | `downloader/downloader.py` | ✅ DONE |
| BUG-002 | 🔴 | Fix SimpCity missing `base_url` | `downloader/simpcity.py` | ✅ DONE |
| BUG-003 | 🟡 | Remove unused import | `downloader/jpg5.py` | ✅ DONE |
| BUG-004 | 🟡 | Fix EromeDownloader `folder_name` scope | `downloader/erome.py` | ✅ DONE |
| REFACTOR-001 | ✅ | Standardize cancel mechanisms | `downloader/*.py` | DONE |
| REFACTOR-002 | 🟡 | Fix database connection cleanup | `downloader/downloader.py` | ✅ DONE |
| REFACTOR-003 | 🟡 | Fix BunkrDownloader thread shutdown | `downloader/bunkr.py` | ✅ DONE |
| FEATURE-001 | ✅ | Add batch URL input | `app/ui.py` | DONE |
| FEATURE-002 | ✅ | Create BaseDownloader class | `downloader/base.py` | DONE |
| FEATURE-003 | ✅ | Add download queue manager | `downloader/queue.py` | DONE |
| FEATURE-004 | ✅ | Add proxy support | `app/settings_window.py`, downloaders | DONE |
| FEATURE-005 | 🟡 | Add bandwidth limiting | All downloaders | Medium |
| FEATURE-006 | 🟡 | Add file size filter | All downloaders | Low |
| FEATURE-007 | 🟡 | Add date range filter | `downloader/downloader.py` | Medium |
| FEATURE-YTDLP | ✅ | Add yt-dlp universal support | `downloader/ytdlp_adapter.py` | DONE |
| FEATURE-GALLERY | ✅ | Add gallery-dl support | `downloader/gallery.py` | DONE |
| FEATURE-RETRY | ✅ | Add retry policies | `downloader/policies.py` | DONE |
| FEATURE-RATELIMIT | ✅ | Add per-domain rate limiting | `downloader/ratelimiter.py` | DONE |
| ARCH-001 | 🟠 | Split ui.py into modules | `app/ui.py` → `app/window/` | High |
| TEST-001 | ✅ | Add unit test infrastructure | `tests/` | DONE |
| TEST-002 | ✅ | Add type hints (main app complete) | All Python files | DONE |

---

## Bug Fixes

### BUG-001: Fix undefined `log_message` variable

```
PRIORITY: 🔴 CRITICAL
FILE: downloader/downloader.py
LOCATION: safe_request() method, exception handler for status codes 429, 500-504

PROBLEM:
The variable `log_message` is used before being defined in the exception handler.
This causes NameError when the server returns 429/500-504 status codes.

SOLUTION:
Define `log_message` before the `self.log(log_message)` call.

FIND THIS CODE:
    # Look for exception handling block that calls self.log(log_message)
    # where log_message hasn't been assigned yet

FIX:
    log_message = f"Server error {status_code}, retrying..."
    self.log(log_message)

DONE WHEN:
- [ ] No NameError when server returns 429 status
- [ ] No NameError when server returns 500-504 status
- [ ] Appropriate error message is logged

TEST:
    python main.py
    # Try downloading from a URL that might rate limit
```

---

### BUG-002: Fix SimpCity missing `base_url`

```
PRIORITY: 🔴 CRITICAL
FILE: downloader/simpcity.py
LOCATION: process_page() method

PROBLEM:
`self.base_url` is referenced but never defined.
This causes AttributeError when handling pagination on multi-page threads.

SOLUTION:
Set self.base_url from the initial URL before calling process_page().

FIND THIS CODE:
    self.process_page(self.base_url + next_page_url)

ADD BEFORE process_page() is first called:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    self.base_url = f"{parsed.scheme}://{parsed.netloc}"

DONE WHEN:
- [ ] self.base_url is set before process_page() is called
- [ ] Pagination works on multi-page SimpCity threads
- [ ] No AttributeError during download

TEST:
    python main.py
    # Enter a multi-page SimpCity thread URL
```

---

### BUG-003: Remove unused import

```
PRIORITY: 🟡 MEDIUM
FILE: downloader/jpg5.py
LOCATION: Top of file

PROBLEM:
`from app import progress_manager` is imported but never used.

SOLUTION:
Delete the import line.

FIND THIS CODE:
    from app import progress_manager

FIX:
    # Delete this line

DONE WHEN:
- [ ] Unused import removed
- [ ] File still runs without errors

TEST:
    python -c "from downloader.jpg5 import Jpg5Downloader; print('OK')"
```

---

### BUG-004: Fix EromeDownloader `folder_name` scope

```
PRIORITY: 🟡 MEDIUM
FILE: downloader/erome.py
LOCATION: process_album_page() method

PROBLEM:
`folder_name` may be undefined when direct_download is True,
causing NameError in the log statement.

SOLUTION:
Initialize folder_name with a default value before the conditional block.

FIND THIS CODE:
    self.log(self.tr("Album download complete: {folder_name}", folder_name=folder_name))

FIX:
    # Add at the start of the method:
    folder_name = "direct_download"
    
    # Then the existing conditional logic can override it

DONE WHEN:
- [ ] folder_name is always defined when logging
- [ ] No NameError when direct_download is True
- [ ] Download completes successfully

TEST:
    python main.py
    # Enter an Erome direct download URL
```

---

## Refactoring Tasks

### REFACTOR-001: Standardize cancel mechanisms

```
PRIORITY: 🟠 HIGH
FILES: 
  - downloader/bunkr.py
  - downloader/erome.py
  - downloader/simpcity.py

PROBLEM:
Inconsistent cancellation patterns across downloaders:
- downloader.py: threading.Event() ✓ (correct)
- jpg5.py: threading.Event() ✓ (correct)
- bunkr.py: self.cancel_requested = False (not thread-safe)
- erome.py: self.cancel_requested = False (not thread-safe)
- simpcity.py: self.cancel_requested = False (not thread-safe)

SOLUTION:
Convert all boolean flag cancellation to threading.Event() pattern.

FOR EACH FILE (bunkr.py, erome.py, simpcity.py):

1. FIND in __init__:
       self.cancel_requested = False
   REPLACE WITH:
       self.cancel_event = threading.Event()

2. FIND all occurrences of:
       self.cancel_requested = True
   REPLACE WITH:
       self.cancel_event.set()

3. FIND all occurrences of:
       if self.cancel_requested:
   REPLACE WITH:
       if self.cancel_event.is_set():

4. ADD import if not present:
       import threading

DONE WHEN:
- [ ] All 3 files use threading.Event()
- [ ] Cancel works correctly in all downloaders
- [ ] No race conditions during cancellation

TEST:
    python main.py
    # Start a download, click cancel, verify it stops cleanly
```

---

### REFACTOR-002: Fix database connection cleanup

```
PRIORITY: 🟡 MEDIUM
FILE: downloader/downloader.py

PROBLEM:
Database connection opened in init_db() is never explicitly closed.
This can cause resource leaks.

SOLUTION:
Add cleanup in shutdown_executor() method.

FIND shutdown_executor() method and ADD:
    if hasattr(self, 'conn') and self.conn:
        self.conn.close()
        self.conn = None

DONE WHEN:
- [ ] Database connection closed on shutdown
- [ ] No SQLite resource warnings
- [ ] Application exits cleanly

TEST:
    python main.py
    # Download something, close the app, check for warnings
```

---

### REFACTOR-003: Fix BunkrDownloader notification thread

```
PRIORITY: 🟡 MEDIUM
FILE: downloader/bunkr.py

PROBLEM:
start_notification_thread() creates a daemon thread that runs indefinitely
with no clean shutdown mechanism.

SOLUTION:
Add a shutdown flag checked in the notification loop.

1. ADD to __init__:
       self._notification_shutdown = threading.Event()

2. MODIFY the notification thread loop to check:
       while not self._notification_shutdown.is_set():
           # existing loop code
           time.sleep(0.1)  # Add small sleep to prevent busy-wait

3. ADD to cancel/completion handling:
       self._notification_shutdown.set()

DONE WHEN:
- [ ] Notification thread stops when download completes
- [ ] Notification thread stops when download is cancelled
- [ ] No orphaned threads

TEST:
    python main.py
    # Download from Bunkr, verify thread count returns to normal after
```

---

## Feature Tasks

### FEATURE-001: Add batch URL input

```
PRIORITY: 🟠 HIGH
FILE: app/ui.py
COMPLEXITY: Medium
DEPENDS ON: None

PROBLEM:
Users can only enter one URL at a time.

SOLUTION:
Replace single-line CTkEntry with multi-line CTkTextbox.

IMPLEMENTATION STEPS:

1. FIND the URL entry widget creation (around line 320-340):
       self.entry_url = ctk.CTkEntry(...)
   
2. REPLACE WITH:
       self.entry_url = ctk.CTkTextbox(
           self.input_frame,
           height=80,
           wrap="none"
       )

3. UPDATE get URL method - FIND:
       url = self.entry_url.get()
   REPLACE WITH:
       url = self.entry_url.get("1.0", "end-1c").strip()

4. ADD URL parsing for multiple lines:
       urls = [line.strip() for line in url.split('\n') if line.strip()]

5. ADD validation before download:
       # Skip empty lines, warn on invalid URLs

DONE WHEN:
- [ ] Multi-line textbox accepts multiple URLs
- [ ] Each URL is processed (can be sequential for now)
- [ ] Empty lines are skipped
- [ ] Invalid URLs show warning

TEST:
    python main.py
    # Paste multiple URLs, verify all are processed
```

---

### FEATURE-002: Create BaseDownloader class ✅ COMPLETED

```
PRIORITY: ✅ COMPLETED
FILE: downloader/base.py
COMPLEXITY: High

STATUS: IMPLEMENTED

The BaseDownloader class has been implemented with:
- Abstract methods: supports_url(), get_site_name(), download()
- Common methods: request_cancel(), is_cancelled(), log(), report_progress()
- Data classes: DownloadOptions, DownloadResult, MediaItem
- can_handle() classmethod for lightweight URL routing

ADDITIONAL IMPLEMENTATIONS:
- downloader/factory.py: DownloaderFactory with 4-tier routing
- downloader/ytdlp_adapter.py: YtDlpDownloader for 1000+ sites
- downloader/gallery.py: GalleryDownloader for image galleries
- downloader/queue.py: DownloadQueueManager with events
- downloader/history.py: SQLite persistence for jobs/events
- downloader/models.py: JobStatus, ItemStatus, DownloadEvent
- downloader/policies.py: RetryPolicy, DomainPolicy
- downloader/ratelimiter.py: Per-domain rate limiting

TESTS: 241 tests in tests/ directory
```

---

## Current State Analysis

### Strengths
- ✅ **Universal Site Support**: 1000+ sites via yt-dlp and gallery-dl integration
- ✅ **Smart URL Routing**: Factory pattern with 4-tier fallback (native → gallery → yt-dlp → generic)
- ✅ **Job Queue System**: Persistent history, crash recovery, event-driven architecture
- ✅ **Press & Forget**: Exponential backoff + jitter, per-domain rate limiting, auto-retry
- ✅ **Browser Cookie Import**: Auto-authenticate from Chrome/Firefox/Edge
- ✅ **Test Infrastructure**: 241 tests, behavior contracts documentation
- **Multi-site support**: Native scrapers for coomer.su, kemono.su, erome.com, bunkr-albums.io, simpcity.su, jpg5.su
- **Multi-threaded downloads**: Configurable concurrent download workers (1-10)
- **Progress tracking**: Real-time progress bars with speed and ETA calculations
- **SQLite database**: Tracks downloaded files to avoid duplicates with caching
- **Multi-language support**: 6 languages (ES, EN, JA, ZH, FR, RU)
- **Theming**: Light/Dark/System theme support via CustomTkinter
- **Cookie management**: For authenticated site access (SimpCity)
- **Flexible file naming**: 4 different naming modes
- **Subdomain fallback**: Automatic subdomain probing for coomer/kemono (n1-n10)
- **Resume support**: Partial download resumption in main downloader
- **Runtime settings**: Hot-reload of settings without restart

### Remaining Limitations
- **Monolithic UI code**: `ui.py` is 1226 lines mixing UI, logic, and state
- **No download queue management UI**: Backend queue system ready, needs UI integration
- **Missing batch URL input**: Must process URLs one at a time (UI limitation)
- **No proxy support**: Missing network configuration options
- **No bandwidth limiting**: Can saturate network connections
- **Missing scheduled downloads**: No timer/scheduler functionality

---

## Detailed Code Analysis

### File Structure Overview

```
CoomerDL/
├── app/
│   ├── ui.py                 # 1226 lines - Main application window
│   ├── settings_window.py    # 906 lines - Settings modal with 5 tabs
│   ├── progress_manager.py   # 192 lines - Download progress tracking
│   ├── about_window.py       # 185 lines - About dialog
│   └── donors.py             # 222 lines - Patreon supporters modal
├── downloader/
│   ├── downloader.py         # 725 lines - Core downloader (coomer/kemono)
│   ├── bunkr.py              # 360 lines - Bunkr downloader
│   ├── erome.py              # 288 lines - Erome downloader
│   ├── simpcity.py           # 138 lines - SimpCity downloader
│   └── jpg5.py               # 112 lines - Jpg5 downloader
└── resources/
    ├── config/               # JSON configs, SQLite DB, cookies
    ├── img/                  # Icons and assets
    └── ...
```

### Component Analysis

#### 1. Main UI (`app/ui.py`) - 1226 lines

**Key Functions:**
| Function | Lines | Purpose | Issues |
|----------|-------|---------|--------|
| `__init__` | 60-178 | App initialization | Too many responsibilities |
| `initialize_ui` | 289-421 | UI component creation | Mixed with event handling |
| `create_custom_menubar` | 483-591 | Menu bar creation | Contains inline event handlers |
| `start_download` | 774-862 | URL routing to downloaders | Complex conditional logic |
| `add_log_message_safe` | 913-937 | Thread-safe logging | Error handling could be cleaner |

**State Management Issues:**
- Multiple downloader instances created per download
- `active_downloader` variable tracks current download but no queue
- Settings loaded in multiple places (init, settings_window)

**UI Components:**
- Custom menu bar (CTkFrame-based, not native)
- URL entry (single line CTkEntry)
- Download options checkboxes
- Progress bar with percentage display
- Log textbox with autoscroll option
- Footer with speed/ETA labels

#### 2. Core Downloader (`downloader/downloader.py`) - 725 lines

**Key Features:**
- ThreadPoolExecutor for concurrent downloads
- SQLite-based download tracking with caching
- Domain-based rate limiting with semaphores
- Subdomain fallback for 403/404 errors
- Resume support with Range headers
- 4 file naming modes

**Key Methods:**
| Method | Lines | Purpose |
|--------|-------|---------|
| `init_db` | 74-88 | SQLite schema creation |
| `safe_request` | 138-220 | Rate-limited HTTP requests |
| `_find_valid_subdomain` | 222-263 | Subdomain probing (n1-n10) |
| `fetch_user_posts` | 265-312 | API pagination handling |
| `process_media_element` | 407-562 | Single file download with resume |
| `download_media` | 578-664 | Batch download orchestration |

**Database Schema:**
```sql
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_url TEXT UNIQUE,
    file_path TEXT,
    file_size INTEGER,
    user_id TEXT,
    post_id TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 3. Site-Specific Downloaders Comparison

| Feature | downloader.py | bunkr.py | erome.py | simpcity.py | ytdlp_adapter.py | gallery.py |
|---------|--------------|----------|----------|-------------|------------------|------------|
| Base class | BaseDownloader | BaseDownloader | BaseDownloader | BaseDownloader | BaseDownloader | BaseDownloader |
| Cancel mechanism | Event | Event | Event | Event | Event | Event |
| Progress callback | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Retry mechanism | ✓ (policies) | ✓ (policies) | ✓ (policies) | ✓ (policies) | ✓ (yt-dlp native) | ✓ (gallery-dl native) |
| Resume support | ✓ | ✗ | ✗ | ✗ | ✓ (yt-dlp) | ✓ (gallery-dl) |
| Database tracking | ✓ | ✗ | ✗ | ✗ | ✓ (history.py) | ✓ (history.py) |
| Translation support | ✓ | ✓ (partial) | ✓ | ✓ | ✓ | ✓ |
| Session reuse | ✓ | ✓ | ✓ | cloudscraper | N/A | N/A |
| Rate limiting | ✓ (ratelimiter) | ✓ (ratelimiter) | ✓ (ratelimiter) | ✓ (ratelimiter) | ✓ (yt-dlp native) | ✓ (gallery-dl native) |
| Site coverage | 2 | 1 | 1 | 1 | 1000+ | 100+ |

#### 4. Settings Window (`app/settings_window.py`)

**Tabs:**
1. **General**: Theme, language, update check
2. **Downloads**: Max downloads, folder structure, retries, file naming
3. **Structure**: Visual folder structure preview
4. **Database**: Download history treeview
5. **Cookies**: SimpCity cookie management
6. **Universal (yt-dlp)** ✅ NEW: FFmpeg status, format selection, container, metadata options, browser cookie import

**Configuration Storage:**
- Path: `resources/config/settings.json`
- Default values: `{'max_downloads': 3, 'folder_structure': 'default', 'language': 'en', 'theme': 'System'}`

#### 5. Progress Manager (`app/progress_manager.py`) - 192 lines

**Features:**
- Global progress bar in main window
- Per-file progress in popup window
- Speed/ETA calculation and display
- Automatic cleanup of completed downloads

**Key Issue:** Progress window uses `grab_set()` which can block other windows.

#### 6. Job Queue System ✅ NEW

**Components:**
- `downloader/models.py`: JobStatus, ItemStatus, DownloadEventType, DownloadJob, DownloadEvent
- `downloader/history.py`: DownloadHistoryDB with SQLite persistence
- `downloader/queue.py`: DownloadQueueManager with event callbacks

**Event-Driven Architecture:**
- Backend emits: JOB_ADDED, JOB_STARTED, JOB_PROGRESS, ITEM_PROGRESS, ITEM_DONE, JOB_DONE, JOB_ERROR, LOG
- UI subscribes to events for updates
- No Tkinter dependency in backend

### Identified Code Patterns

#### Good Patterns:
1. **Thread-safe logging**: `add_log_message_safe` uses queue pattern
2. **Callback-based architecture**: Loose coupling between components
3. **Graceful degradation**: Offline mode detection for GitHub API
4. **Consistent file sanitization**: `re.sub(r'[<>:"/\\|?*]', '_', filename)`
5. ✅ **Event-driven backend**: Queue system emits events, UI subscribes
6. ✅ **Factory pattern**: Lightweight `can_handle()` classmethod routing
7. ✅ **Policy-based retry**: Exponential backoff + jitter via `RetryPolicy`
8. ✅ **Domain rate limiting**: Per-domain concurrency and delays via `DomainLimiter`

#### Anti-Patterns (Remaining):
1. **God class**: `ImageDownloaderApp` handles too many responsibilities
2. **Duplicated code**: File extension checks repeated across downloaders
3. **Magic numbers**: Chunk sizes (65536, 1048576) hardcoded
4. **Inconsistent error handling**: Some exceptions silently caught
5. **Mixed languages in code**: Spanish comments/strings mixed with English

---

## Technical Debt

### Critical Issues

1. **Undefined variable in `Downloader.safe_request()` method**
   ```python
   self.log(log_message)  # log_message not defined at this point
   ```
   - Location: `downloader/downloader.py`, inside exception handler for status codes 429, 500-504
   - Fix: Define `log_message` before use or restructure error handling

2. **SimpCity missing base_url in `process_page()` method**
   ```python
   self.process_page(self.base_url + next_page_url)  # self.base_url never set
   ```
   - Location: `downloader/simpcity.py`, `process_page()` method when handling pagination
   - Fix: Extract and store base URL from initial URL in `download_images_from_simpcity()`

3. **Jpg5Downloader unused import**
   ```python
   from app import progress_manager  # Unused import
   ```
   - Location: `downloader/jpg5.py`, top of file
   - Fix: Remove unused import or integrate progress_manager properly

### Medium Priority

4. **Inconsistent cancel mechanisms across downloaders**
   - `Downloader`: `threading.Event()` (proper)
   - `BunkrDownloader`: `self.cancel_requested = False` (boolean flag)
   - `EromeDownloader`: `self.cancel_requested = False` (boolean flag)
   - `SimpCity`: `self.cancel_requested = False` (boolean flag)
   - `Jpg5Downloader`: `threading.Event()` (proper)
   - Fix: Standardize all to Event-based cancellation for thread-safety

5. **Database connection not closed properly**
   - Location: `Downloader.init_db()` keeps connection open indefinitely
   - No `__del__` method or context manager implementation
   - Fix: Use context manager pattern or explicit cleanup in `shutdown_executor()`

6. **BunkrDownloader notification thread in `start_notification_thread()`**
   - Daemon thread runs indefinitely polling `log_messages` list
   - No clean shutdown mechanism when cancelling
   - Fix: Add shutdown flag checked in loop or use different logging pattern

7. **EromeDownloader folder_name scope issue in `process_album_page()`**
   ```python
   self.log(self.tr("Album download complete: {folder_name}", folder_name=folder_name))
   # folder_name may be undefined if direct_download is True
   ```
   - Fix: Initialize `folder_name` with default before conditional block

### Low Priority

8. **Hardcoded user agents across downloaders**
   - Different user agents in each downloader class
   - Fix: Centralize user agent configuration in settings or constants

9. **Mixed chunk sizes for downloads**
   - `Downloader`: 1048576 bytes (1MB)
   - `BunkrDownloader`: 65536 bytes (64KB)
   - `EromeDownloader`: 65536 bytes (64KB)
   - `Jpg5Downloader`: 1024 bytes (1KB)
   - Fix: Make chunk size configurable via settings

10. **Inconsistent path handling**
    - Some use `os.path.join`, others concatenate strings
    - Fix: Standardize to `pathlib.Path`

---

## UI/UX Improvements

### 1. Main Window Redesign
**Priority: High**

```
┌─────────────────────────────────────────────────────────────────┐
│  [File ▼] [Settings ▼] [Help ▼]          🌙 [Discord] [GitHub] │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ URL Input (multi-line textarea for batch URLs)            │  │
│  │ Drag & Drop zone for URL lists                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  [📁 Select Folder] [Download Path Display]                     │
│                                                                 │
│  ┌─ Download Options ─────────────────────────────────────────┐ │
│  │ ☑ Images  ☑ Videos  ☑ Documents  ☑ Archives               │ │
│  │ [▼ Quality] [▼ Date Range] [▼ Custom Filters]             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [▶ Download] [⏸ Pause All] [⏹ Cancel All] [📋 Queue (5)]     │
│                                                                 │
│  ┌─ Active Downloads ─────────────────────────────────────────┐ │
│  │ ┌──────────────────────────────────────────────────────┐   │ │
│  │ │ 🎬 video_001.mp4    [████████░░] 78%  2.3MB/s  1:23  │   │ │
│  │ │ 🖼 image_002.jpg    [██████████] 100% Done           │   │ │
│  │ └──────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ Logs ────────────────────────────────────────────────────┐  │
│  │ [Filter: All ▼] [Search 🔍]  [Clear] [Export]             │  │
│  │ ─────────────────────────────────────────────────────────  │  │
│  │ 12:34:56 INFO  Starting download from profile xyz...      │  │
│  │ 12:34:57 INFO  Found 45 media files                       │  │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Speed: 5.2 MB/s | ETA: 5:23 | Completed: 12/45 | Errors: 0     │
└─────────────────────────────────────────────────────────────────┘
```

**Proposed Changes:**
- [ ] Multi-line URL input for batch downloads
- [ ] Drag & drop support for URL lists (text files)
- [ ] Download queue panel with pause/resume/cancel per item
- [ ] Searchable/filterable log panel
- [ ] Enhanced status bar with more metrics
- [ ] Collapsible sections for cleaner layout
- [ ] Keyboard shortcuts (Ctrl+V paste, Ctrl+Enter download)

### 2. Settings Window Improvements
**Priority: Medium**

**Proposed Changes:**
- [ ] Reorganize into clearer categories with icons
- [ ] Add preview panels (folder structure preview already exists)
- [ ] Add profile presets (save/load settings configurations)
- [ ] Add import/export settings functionality
- [ ] Better validation and feedback for user inputs
- [ ] Reset to defaults option per section

### 3. Download Queue Manager
**Priority: High**

**New Feature:**
- [ ] Dedicated queue management window
- [ ] Drag-and-drop reordering
- [ ] Individual item controls (pause, resume, cancel, retry)
- [ ] Priority levels (high, normal, low)
- [ ] Queue persistence across app restarts
- [ ] Batch operations (select multiple, remove completed)

### 4. Download History Browser
**Priority: Medium**

**New Feature:**
- [ ] Enhanced database viewer with search/filter
- [ ] Thumbnail previews for downloaded media
- [ ] Open file/folder from history
- [ ] Re-download capability
- [ ] Statistics dashboard (total downloaded, by site, by type)
- [ ] Export history to CSV/JSON

### 5. Visual Feedback Improvements
**Priority: Medium**

**Proposed Changes:**
- [ ] Toast notifications for completed downloads
- [ ] System tray integration (minimize to tray, notifications)
- [ ] Sound notifications (optional)
- [ ] Color-coded log messages (info, warning, error)
- [ ] Animated icons during downloads
- [ ] Progress in window title bar

---

## Feature Enhancements

### 1. Batch URL Processing
**Priority: High**

**New Feature:**
- [ ] Multi-line URL input
- [ ] Import URLs from text file
- [ ] URL validation before download
- [ ] Duplicate URL detection
- [ ] Pattern-based URL generation (e.g., user profiles pagination)

### 2. Advanced Filtering
**Priority: Medium**

**New Features:**
- [ ] Filter by file size (min/max)
- [ ] Filter by date range (posted date)
- [ ] Filter by file extension (beyond type categories)
- [ ] Custom regex patterns for filenames
- [ ] Exclude patterns (skip files matching criteria)
- [ ] Save filter presets

### 3. Network Configuration
**Priority: Medium**

**New Features:**
- [ ] Proxy support (HTTP, SOCKS)
- [ ] Bandwidth limiting (max download speed)
- [ ] Connection timeout settings
- [ ] Retry configuration per-site
- [ ] User-Agent customization
- [ ] Rate limiting configuration

### 4. Scheduling & Automation
**Priority: Low**

**New Features:**
- [ ] Scheduled downloads (time-based)
- [ ] Watch folders for URL lists
- [ ] Post-download actions (move, organize, notify)
- [ ] Command-line interface for scripting
- [ ] Auto-start with system (optional)

### 5. Site-Specific Features
**Priority: Medium**

**Enhancements:**
- [ ] **Coomer/Kemono**: Favorite users tracking, new post notifications
- [ ] **Erome**: Album detection improvements
- [ ] **Bunkr**: Better file type detection
- [ ] **SimpCity**: Thread pagination improvements
- [ ] **Jpg5**: Gallery support

### 6. Media Organization
**Priority: Medium**

**New Features:**
- [ ] Custom folder structure templates
- [ ] Metadata extraction (EXIF for images)
- [ ] Auto-rename based on metadata
- [ ] Duplicate detection (hash-based)
- [ ] Archive management (auto-extract)

---

## Architecture Improvements

### 1. Refactor UI Components
**Priority: High**

**Current Structure:**
```
ui.py (1226 lines)
├── Window setup
├── Menu bar creation
├── Input frame
├── Options frame
├── Action frame
├── Log textbox
├── Progress management
├── Download orchestration
├── URL parsing
├── Settings management
└── Utility functions
```

**Proposed Structure:**
```
app/
├── main.py                    # Entry point
├── window/
│   ├── __init__.py
│   ├── main_window.py         # CTk root window
│   ├── menu_bar.py            # Custom menu bar
│   ├── input_panel.py         # URL input, folder selection
│   ├── options_panel.py       # Download options checkboxes
│   ├── action_panel.py        # Download/Cancel buttons
│   ├── log_panel.py           # Log textbox with controls
│   ├── progress_panel.py      # Progress bars
│   └── status_bar.py          # Footer with speed/ETA
├── dialogs/
│   ├── __init__.py
│   ├── settings_dialog.py     # Settings window
│   ├── about_dialog.py        # About window
│   ├── donors_dialog.py       # Donors modal
│   └── queue_dialog.py        # NEW: Queue manager
├── models/
│   ├── __init__.py
│   ├── download_item.py       # Download item data class
│   ├── settings.py            # Settings model with validation
│   └── download_queue.py      # Queue management
└── utils/
    ├── __init__.py
    ├── translations.py        # Translation utilities
    ├── url_parser.py          # URL parsing and validation
    └── file_utils.py          # File operations
```

### 2. Standardize Downloader Interface
**Priority: High**

**Proposed Base Class:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Callable
from enum import Enum
import threading

class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DownloadOptions:
    download_images: bool = True
    download_videos: bool = True
    download_compressed: bool = True
    max_retries: int = 3
    retry_interval: float = 2.0
    chunk_size: int = 1048576
    timeout: int = 30

@dataclass
class MediaItem:
    url: str
    filename: str
    file_type: str  # 'image', 'video', 'document', 'compressed', 'other'
    size: Optional[int] = None
    post_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class DownloadResult:
    success: bool
    total_files: int
    completed_files: int
    failed_files: List[str]
    skipped_files: List[str]
    error_message: Optional[str] = None

class BaseDownloader(ABC):
    """Abstract base class for all site-specific downloaders."""
    
    def __init__(
        self,
        download_folder: str,
        options: DownloadOptions = None,
        log_callback: Callable[[str], None] = None,
        progress_callback: Callable[[int, int, dict], None] = None,
        global_progress_callback: Callable[[int, int], None] = None,
    ):
        self.download_folder = download_folder
        self.options = options or DownloadOptions()
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.global_progress_callback = global_progress_callback
        self.cancel_event = threading.Event()
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = []
        self.skipped_files = []
    
    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """Check if this downloader can handle the given URL."""
        pass
    
    @abstractmethod
    def get_media_urls(self, url: str) -> List[MediaItem]:
        """Extract media URLs from a page without downloading."""
        pass
    
    @abstractmethod
    def download_profile(self, url: str) -> DownloadResult:
        """Download all media from a user profile."""
        pass
    
    @abstractmethod
    def download_post(self, url: str) -> DownloadResult:
        """Download media from a single post."""
        pass
    
    def request_cancel(self):
        """Request cancellation of current download."""
        self.cancel_event.set()
        self.log("Download cancellation requested.")
    
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self.cancel_event.is_set()
    
    def log(self, message: str):
        """Log a message through the callback."""
        if self.log_callback:
            self.log_callback(message)
    
    def report_progress(self, downloaded: int, total: int, **kwargs):
        """Report download progress through the callback."""
        if self.progress_callback:
            self.progress_callback(downloaded, total, kwargs)
    
    def report_global_progress(self):
        """Report overall progress through the callback."""
        if self.global_progress_callback:
            self.global_progress_callback(self.completed_files, self.total_files)
```

**Downloader Factory:**
```python
class DownloaderFactory:
    """Factory for creating appropriate downloader based on URL."""
    
    _downloaders = []
    
    @classmethod
    def register(cls, downloader_class):
        """Decorator to register a downloader class."""
        cls._downloaders.append(downloader_class)
        return downloader_class
    
    @classmethod
    def get_downloader(cls, url: str, **kwargs) -> Optional[BaseDownloader]:
        """Get appropriate downloader for the given URL."""
        for downloader_class in cls._downloaders:
            instance = downloader_class(**kwargs)
            if instance.supports_url(url):
                return instance
        return None

# Usage:
@DownloaderFactory.register
class CoomerDownloader(BaseDownloader):
    def supports_url(self, url: str) -> bool:
        # Supports both coomer and kemono sites
        return any(domain in url for domain in ["coomer.su", "coomer.st", "kemono.su", "kemono.cr"])
    # ... implementation
```

### 3. Configuration Management
**Priority: Medium**

**Proposed Configuration Class:**
```python
from dataclasses import dataclass, field, asdict
from typing import Dict, Any
import json
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration with validation."""
    
    # General
    language: str = "en"
    theme: str = "System"  # Light, Dark, System
    
    # Downloads
    max_downloads: int = 3
    folder_structure: str = "default"  # default, post_number
    max_retries: int = 3
    retry_interval: float = 2.0
    file_naming_mode: int = 0  # 0-3
    
    # Network (NEW)
    proxy_enabled: bool = False
    proxy_url: str = ""
    bandwidth_limit: int = 0  # 0 = unlimited, otherwise KB/s
    connection_timeout: int = 30
    
    # UI (NEW)
    window_width: int = 1000
    window_height: int = 600
    autoscroll_logs: bool = False
    
    CONFIG_PATH = Path("resources/config/settings.json")
    
    def __post_init__(self):
        """Validate configuration values."""
        self.max_downloads = max(1, min(10, self.max_downloads))
        self.max_retries = max(0, self.max_retries)
        self.retry_interval = max(0.1, self.retry_interval)
        self.file_naming_mode = max(0, min(3, self.file_naming_mode))
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from file."""
        if cls.CONFIG_PATH.exists():
            try:
                with open(cls.CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, TypeError) as e:
                # Log error but continue with defaults
                print(f"Warning: Could not load config: {e}")
        return cls()
    
    def save(self):
        """Save configuration to file."""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, 'w') as f:
            json.dump(asdict(self), f, indent=4)
```

### 4. Logging System
**Priority: Medium**

**Proposed Implementation:**
```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

class AppLogger:
    """Centralized logging with file rotation and UI callback."""
    
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.logger = logging.getLogger("CoomerDL")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation (uses TimedRotatingFileHandler for daily logs)
        log_dir = Path("resources/config/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Use a fixed base name; rotation handles date-based files
        file_handler = RotatingFileHandler(
            log_dir / "coomer.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
        # UI handler
        if ui_callback:
            ui_handler = UILogHandler(ui_callback)
            ui_handler.setLevel(logging.INFO)
            self.logger.addHandler(ui_handler)
    
    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)

class UILogHandler(logging.Handler):
    """Custom handler to send logs to UI."""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    
    def emit(self, record):
        msg = self.format(record)
        if self.callback:
            self.callback(msg)
```

### 5. Database Improvements
**Priority: Low**

**Proposed Schema Expansion:**
```sql
-- Current table (preserved)
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_url TEXT UNIQUE,
    file_path TEXT,
    file_size INTEGER,
    user_id TEXT,
    post_id TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Index for faster queries
CREATE INDEX idx_downloads_user ON downloads(user_id);
CREATE INDEX idx_downloads_post ON downloads(post_id);
CREATE INDEX idx_downloads_date ON downloads(downloaded_at);

-- NEW: Users table for tracking
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    site TEXT,  -- 'coomer', 'kemono', 'erome', etc.
    username TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE
);

-- NEW: Download sessions for statistics
CREATE TABLE download_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    url TEXT,
    site TEXT,
    total_files INTEGER,
    completed_files INTEGER,
    failed_files INTEGER,
    skipped_files INTEGER,
    total_bytes INTEGER
);
```

---

## Performance Optimizations

### 1. Download Performance
**Priority: Medium**

**Proposed Changes:**
- [ ] Connection pooling optimization
- [ ] Chunk size configuration
- [ ] Resume support for all downloaders
- [ ] Memory usage optimization for large files
- [ ] Async download implementation (optional)

### 2. UI Performance
**Priority: Medium**

**Proposed Changes:**
- [ ] Lazy loading for history/database views
- [ ] Virtual scrolling for large lists
- [ ] Debounced UI updates
- [ ] Background thread for non-UI operations
- [ ] Progress update throttling

### 3. Resource Management
**Priority: Low**

**Proposed Changes:**
- [ ] Image caching for thumbnails
- [ ] Proper cleanup on app close
- [ ] Memory profiling and optimization
- [ ] Disk cache for parsed pages

---

## Configuration & Customization

### 1. User Preferences
**Priority: Medium**

**New Options:**
- [ ] Customizable keyboard shortcuts
- [ ] Window position/size persistence
- [ ] Custom themes (color schemes)
- [ ] Font size adjustment
- [ ] Column visibility in lists

### 2. Download Presets
**Priority: Low**

**New Feature:**
- [ ] Save download configurations as presets
- [ ] Quick-access preset buttons
- [ ] Import/export presets
- [ ] Per-site default presets

### 3. Advanced Settings
**Priority: Low**

**New Options:**
- [ ] Debug mode toggle
- [ ] Performance tuning options
- [ ] Experimental features toggle
- [ ] Developer options (network logging, etc.)

---

## Testing & Quality

### 1. Test Infrastructure
**Priority: High**

**Proposed Implementation:**
- [ ] Unit tests for downloaders
- [ ] UI tests (pytest-qt or similar)
- [ ] Integration tests for end-to-end flows
- [ ] Mock servers for testing without network

### 2. Code Quality
**Priority: Medium**

**Proposed Implementation:**
- [ ] Add type hints throughout codebase
- [ ] Implement linting (flake8, pylint)
- [ ] Add code formatting (black)
- [ ] Documentation strings for all public methods
- [ ] CI/CD pipeline for automated testing

### 3. Error Handling
**Priority: High**

**Proposed Changes:**
- [x] ✅ Comprehensive exception handling (via RetryPolicy)
- [ ] User-friendly error messages
- [ ] Error reporting mechanism
- [x] ✅ Crash recovery (via history.py job_items table)
- [x] ✅ Graceful degradation (via fallback routing)

---

## Implementation Priority

### Phase 1: Foundation ✅ COMPLETED
1. ~~**Refactor UI architecture**~~ - Partial (backend decoupled, UI still monolithic)
2. ✅ **Standardize downloader interface** - BaseDownloader class created
3. **Batch URL support** - Still needed in UI
4. ✅ **Download queue manager** - Backend implemented (DownloadQueueManager)
5. ✅ **Test infrastructure** - 241 tests in tests/

### Phase 2: Universal Engine ✅ COMPLETED
1. ✅ **yt-dlp integration** - YtDlpDownloader (1000+ sites)
2. ✅ **gallery-dl integration** - GalleryDownloader (100+ galleries)
3. ✅ **Smart factory routing** - 4-tier fallback pattern
4. ✅ **Press & forget hardening** - RetryPolicy, DomainLimiter
5. ✅ **Job history/persistence** - SQLite with crash recovery

### Phase 3: UI Integration (Current Priority)
1. **Batch URL support UI** - Multi-line input
2. **Queue manager UI** - Connect to backend DownloadQueueManager
3. **History browser UI** - Connect to backend DownloadHistoryDB
4. **Progress events UI** - Subscribe to JOB_PROGRESS, ITEM_PROGRESS events
5. **Split ui.py into modules** - Use event-driven architecture

### Phase 4: Network & Filters (Medium Priority)
1. **Proxy support** - Network configuration options
2. **Bandwidth limiting** - Download speed caps
3. **Advanced filtering** - Size, date, custom patterns
4. **Enhanced settings** - Reorganization, presets

### Phase 5: Advanced Features (Lower Priority)
1. **Scheduling** - Time-based downloads
2. **System integration** - Tray, notifications
3. **Site-specific enhancements** - Per-site features
4. **Performance optimization** - Async, caching
5. **Custom themes** - User-defined appearance

---

## Notes for Implementation

### Breaking Changes to Consider
- Settings file format changes may require migration
- Database schema changes need upgrade path
- Downloader API changes affect custom extensions

### Backwards Compatibility
- Preserve existing settings when possible
- Provide import tool for old configurations
- Document all breaking changes

### Dependencies to Evaluate
- Consider `httpx` for HTTP client (can replace requests)
  - Benefits: Native async/await support, HTTP/2 support, connection pooling
  - Note: httpx also supports synchronous usage, allowing gradual migration
- Consider `pydantic` for settings validation
  - Benefits: Type safety, automatic validation, serialization
- Evaluate `ttkbootstrap` for enhanced theming
  - Benefits: Modern Bootstrap-like themes, consistent styling
- Consider `pyinstaller` hooks for new dependencies

---

## Feedback & Contributions

This roadmap is a starting point for discussion. Areas that need community input:

1. **Feature prioritization** - What matters most to users?
2. **Site support requests** - Which new sites to add?
3. **UI preferences** - What layout works best?
4. **Performance concerns** - What's slow or resource-heavy?

---

## Agent-Optimized Task Format Reference

All tasks in this document follow this format for easy parsing by AI agents:

```
### TASK-ID: Short Description

PRIORITY: 🔴|🟠|🟡|🟢
FILE: path/to/file.py
LOCATION: method_name() or line numbers (optional)
DEPENDS ON: TASK-IDs (optional)
COMPLEXITY: Low|Medium|High

PROBLEM:
Clear description of what's wrong or what's needed.

SOLUTION:
Concise description of the fix/implementation.

FIND THIS CODE: (for modifications)
    exact code to find

REPLACE WITH: (or ADD:)
    exact replacement code

DONE WHEN:
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

TEST:
    commands to verify the fix works
```

### Key Patterns for Agents

**For bug fixes**: Look for `FIND THIS CODE` and `REPLACE WITH` sections.

**For new features**: Check `SPECIFICATIONS.md` for full class/function definitions.

**For refactoring**: Follow numbered implementation steps.

**Before starting any task**: Check `POTENTIAL_ISSUES.md` for known blockers.

---

## Quick Copy-Paste Prompts for AI Agents

### Fix All Critical Bugs
```
Read ROADMAP.md. Find all 🔴 CRITICAL priority tasks.
For each one:
1. Read the PROBLEM and SOLUTION sections
2. Find the code in the specified FILE
3. Apply the fix
4. Verify with the TEST command

Start with BUG-001, then BUG-002.
```

### Implement a Specific Task
```
Read ROADMAP.md task [TASK-ID].

Context:
- This is a Python desktop app using CustomTkinter for UI
- The app downloads media from various websites
- Follow the coding patterns already in the codebase

Implementation:
1. Check DEPENDS ON - complete prerequisites first
2. Read the PROBLEM and SOLUTION sections carefully  
3. If FILE says "(NEW FILE)", check SPECIFICATIONS.md for full implementation
4. Make the minimal changes to satisfy DONE WHEN criteria
5. Run the TEST command to verify
```

### Code Review a Change
```
Read ROADMAP.md task [TASK-ID] and POTENTIAL_ISSUES.md.

Review this code change:
[paste code here]

Check:
1. Does it satisfy all DONE WHEN criteria?
2. Does it avoid issues listed in POTENTIAL_ISSUES.md?
3. Does it follow existing code patterns in the repository?
4. Is it the minimal change needed?
```

---

## Related Documentation

| Document | When to Use |
|----------|-------------|
| [TASKS.md](TASKS.md) | Full task details with context and dependencies |
| [SPECIFICATIONS.md](SPECIFICATIONS.md) | New class/function implementations |
| [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md) | Known blockers and edge cases |
| [README.md](README.md) | Project overview and setup |
| [tests/CONTRACTS.md](tests/CONTRACTS.md) | System behavior contracts and invariants |

---

## New Architecture Reference

### Download System Architecture (v2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer (Tkinter)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ URL Input   │  │ Queue View  │  │ Progress Display        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                           │                                      │
│                    Subscribes to Events                          │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                    Event Bus (Callbacks)                         │
│  JOB_ADDED │ JOB_STARTED │ ITEM_PROGRESS │ JOB_DONE │ LOG       │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                  DownloadQueueManager                            │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ Job Queue  │  │ Worker Pool  │  │ Event Emitter           │  │
│  └────────────┘  └──────────────┘  └─────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                    DownloaderFactory                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 1. Native Scrapers: Coomer, Kemono, Bunkr, Erome, SimpCity  │ │
│  │ 2. Gallery Engine: gallery-dl (DeviantArt, Pixiv, etc.)     │ │
│  │ 3. Universal Engine: yt-dlp (YouTube, Twitter, Reddit, etc.)│ │
│  │ 4. Generic Fallback: HTML scraper                            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                    BaseDownloader                                │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ Progress   │  │ Cancellation │  │ Rate Limiting           │  │
│  │ Reporting  │  │ (Event)      │  │ (DomainLimiter)         │  │
│  └────────────┘  └──────────────┘  └─────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                    Persistence Layer                             │
│  ┌────────────────────────────────┐  ┌───────────────────────┐  │
│  │ DownloadHistoryDB (SQLite)     │  │ RetryPolicy           │  │
│  │ - jobs table                   │  │ - Exponential backoff │  │
│  │ - events table                 │  │ - Jitter              │  │
│  │ - job_items table (crash rec.) │  │ - Retryable statuses  │  │
│  └────────────────────────────────┘  └───────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Key Files Reference

| File | Purpose |
|------|---------|
| `downloader/base.py` | BaseDownloader abstract class, DownloadOptions, DownloadResult |
| `downloader/factory.py` | Smart URL routing with 4-tier fallback |
| `downloader/ytdlp_adapter.py` | yt-dlp integration (1000+ sites) |
| `downloader/gallery.py` | gallery-dl integration (100+ galleries) |
| `downloader/queue.py` | DownloadQueueManager with job lifecycle |
| `downloader/history.py` | SQLite persistence for jobs, events, crash recovery |
| `downloader/models.py` | JobStatus, ItemStatus, DownloadEvent dataclasses |
| `downloader/policies.py` | RetryPolicy, DomainPolicy configurations |
| `downloader/ratelimiter.py` | Per-domain concurrency and rate limiting |
| `tests/CONTRACTS.md` | System behavior contracts and invariants |

---

*Last updated: December 2024*
*Version: 2.0 (Universal Archiver)*
