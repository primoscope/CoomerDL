# CoomerDL Improvement Roadmap

> **Purpose**: This document outlines proposed improvements for CoomerDL to enable more features, a better UI, and a more adjustable/configurable application. This is a living document that should be refined before implementation.

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Detailed Code Analysis](#detailed-code-analysis)
3. [UI/UX Improvements](#uiux-improvements)
4. [Feature Enhancements](#feature-enhancements)
5. [Architecture Improvements](#architecture-improvements)
6. [Performance Optimizations](#performance-optimizations)
7. [Configuration & Customization](#configuration--customization)
8. [Testing & Quality](#testing--quality)
9. [Technical Debt](#technical-debt)
10. [Implementation Priority](#implementation-priority)

---

## Current State Analysis

### Strengths
- **Multi-site support**: Supports coomer.su, kemono.su, erome.com, bunkr-albums.io, simpcity.su, jpg5.su
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

### Current Limitations
- **Monolithic UI code**: `ui.py` is 1226 lines mixing UI, logic, and state
- **Inconsistent downloader interfaces**: Each site downloader has different constructor signatures and methods
- **Limited error recovery**: Some downloaders lack robust retry mechanisms
- **No download queue management UI**: Can't pause/resume/reorder downloads
- **Missing batch URL input**: Must process URLs one at a time
- **No download history browser**: Database tab shows raw data only
- **Limited filtering options**: Can't filter by date, type, or custom patterns
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

| Feature | downloader.py | bunkr.py | erome.py | simpcity.py | jpg5.py |
|---------|--------------|----------|----------|-------------|---------|
| Base class | None | None | None | None | None |
| Cancel mechanism | Event | Boolean | Boolean | Boolean | Event |
| Progress callback | ✓ | ✓ | ✓ | ✓ | ✓ |
| Retry mechanism | ✓ (configurable) | ✓ (3 fixed) | ✓ (999999) | ✗ | ✗ |
| Resume support | ✓ | ✗ | ✗ | ✗ | ✗ |
| Database tracking | ✓ | ✗ | ✗ | ✗ | ✗ |
| Translation support | ✓ | ✓ (partial) | ✓ | ✓ | ✓ |
| Session reuse | ✓ | ✓ | ✓ | cloudscraper | ✗ |

#### 4. Settings Window (`app/settings_window.py`) - 906 lines

**Tabs:**
1. **General** (515-571): Theme, language, update check
2. **Downloads** (574-708): Max downloads, folder structure, retries, file naming
3. **Structure** (712-766): Visual folder structure preview
4. **Database** (92-165): Download history treeview
5. **Cookies** (167-379): SimpCity cookie management

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

### Identified Code Patterns

#### Good Patterns:
1. **Thread-safe logging**: `add_log_message_safe` uses queue pattern
2. **Callback-based architecture**: Loose coupling between components
3. **Graceful degradation**: Offline mode detection for GitHub API
4. **Consistent file sanitization**: `re.sub(r'[<>:"/\\|?*]', '_', filename)`

#### Anti-Patterns:
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
- [ ] Comprehensive exception handling
- [ ] User-friendly error messages
- [ ] Error reporting mechanism
- [ ] Crash recovery
- [ ] Graceful degradation

---

## Implementation Priority

### Phase 1: Foundation (High Priority)
1. **Refactor UI architecture** - Split monolithic ui.py
2. **Standardize downloader interface** - Create base class
3. **Batch URL support** - Multi-line input
4. **Download queue manager** - Basic queue controls
5. **Test infrastructure** - Basic unit tests

### Phase 2: Core Features (Medium Priority)
1. **Network configuration** - Proxy, bandwidth limiting
2. **Advanced filtering** - Size, date, custom patterns
3. **Enhanced settings** - Reorganization, presets
4. **History browser** - Search, filter, thumbnails
5. **Logging improvements** - Levels, rotation, export

### Phase 3: Advanced Features (Lower Priority)
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

*Last updated: December 2024*
*Version: 0.1 (Draft)*
