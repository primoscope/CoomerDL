# CoomerDL Implementation Specifications

> **Purpose**: Detailed specifications for new tools, functions, classes, and features. Designed for AI coding agents to implement with minimal ambiguity.

---

## Table of Contents

1. [New Classes](#new-classes)
2. [New Functions](#new-functions)
3. [New Modules](#new-modules)
4. [UI Components](#ui-components)
5. [Configuration Schema](#configuration-schema)
6. [Database Schema](#database-schema)
7. [API Contracts](#api-contracts)

---

## New Classes

### 1. BaseDownloader (Abstract Base Class)

**File**: `downloader/base.py` (NEW FILE)

**Purpose**: Standardize all downloader implementations with a common interface.

```python
"""
Base downloader class that all site-specific downloaders must inherit from.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from enum import Enum
import threading


class DownloadStatus(Enum):
    """Status of a download item."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class DownloadOptions:
    """Configuration options for downloads."""
    download_images: bool = True
    download_videos: bool = True
    download_compressed: bool = True
    download_documents: bool = True
    max_retries: int = 3
    retry_interval: float = 2.0
    chunk_size: int = 1048576  # 1MB
    timeout: int = 30
    min_file_size: int = 0  # bytes, 0 = no minimum
    max_file_size: int = 0  # bytes, 0 = no maximum
    date_from: Optional[str] = None  # ISO format YYYY-MM-DD
    date_to: Optional[str] = None  # ISO format YYYY-MM-DD


@dataclass
class MediaItem:
    """Represents a single media file to download."""
    url: str
    filename: str
    file_type: str  # 'image', 'video', 'document', 'compressed', 'other'
    size: Optional[int] = None
    post_id: Optional[str] = None
    user_id: Optional[str] = None
    published_date: Optional[str] = None


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    total_files: int
    completed_files: int
    failed_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    total_bytes: int = 0
    elapsed_seconds: float = 0.0


class BaseDownloader(ABC):
    """
    Abstract base class for all site-specific downloaders.
    
    All downloaders must implement:
    - supports_url(url) -> bool
    - get_site_name() -> str
    - download(url) -> DownloadResult
    
    Provides common functionality:
    - Cancellation via threading.Event
    - Progress reporting via callbacks
    - Logging via callback
    - File type filtering
    """
    
    # Class-level list of supported file extensions by type
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv', '.wmv', '.m4v'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
    COMPRESSED_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz'}
    
    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
        global_progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Initialize the downloader.
        
        Args:
            download_folder: Path to save downloaded files
            options: Download configuration options
            log_callback: Function to call with log messages
            progress_callback: Function to call with per-file progress (downloaded, total, metadata)
            global_progress_callback: Function to call with overall progress (completed, total)
        """
        self.download_folder = download_folder
        self.options = options or DownloadOptions()
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.global_progress_callback = global_progress_callback
        
        # Cancellation mechanism - use Event for thread safety
        self.cancel_event = threading.Event()
        
        # Progress tracking
        self.total_files = 0
        self.completed_files = 0
        self.failed_files: List[str] = []
        self.skipped_files: List[str] = []
    
    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """
        Check if this downloader can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this downloader supports the URL, False otherwise
        """
        pass
    
    @abstractmethod
    def get_site_name(self) -> str:
        """
        Get the human-readable name of the site this downloader handles.
        
        Returns:
            Site name (e.g., "Coomer", "Kemono", "Erome")
        """
        pass
    
    @abstractmethod
    def download(self, url: str) -> DownloadResult:
        """
        Download all media from the given URL.
        
        Args:
            url: The URL to download from (profile, post, or album)
            
        Returns:
            DownloadResult with statistics about the download
        """
        pass
    
    def request_cancel(self) -> None:
        """Request cancellation of the current download."""
        self.cancel_event.set()
        self.log("Download cancellation requested.")
    
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self.cancel_event.is_set()
    
    def reset(self) -> None:
        """Reset the downloader state for a new download."""
        self.cancel_event.clear()
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = []
        self.skipped_files = []
    
    def log(self, message: str) -> None:
        """Log a message through the callback."""
        if self.log_callback:
            self.log_callback(message)
    
    def report_progress(self, downloaded: int, total: int, **kwargs) -> None:
        """Report per-file download progress."""
        if self.progress_callback:
            self.progress_callback(downloaded, total, kwargs)
    
    def report_global_progress(self) -> None:
        """Report overall download progress."""
        if self.global_progress_callback:
            self.global_progress_callback(self.completed_files, self.total_files)
    
    def get_file_type(self, filename: str) -> str:
        """
        Determine file type from extension.
        
        Args:
            filename: The filename to check
            
        Returns:
            One of: 'image', 'video', 'document', 'compressed', 'other'
        """
        ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if ext in self.IMAGE_EXTENSIONS:
            return 'image'
        elif ext in self.VIDEO_EXTENSIONS:
            return 'video'
        elif ext in self.DOCUMENT_EXTENSIONS:
            return 'document'
        elif ext in self.COMPRESSED_EXTENSIONS:
            return 'compressed'
        return 'other'
    
    def should_download_file(self, media_item: MediaItem) -> bool:
        """
        Check if a file should be downloaded based on options.
        
        Args:
            media_item: The media item to check
            
        Returns:
            True if the file should be downloaded, False to skip
        """
        file_type = media_item.file_type or self.get_file_type(media_item.filename)
        
        # Check file type filters
        if file_type == 'image' and not self.options.download_images:
            return False
        if file_type == 'video' and not self.options.download_videos:
            return False
        if file_type == 'document' and not self.options.download_documents:
            return False
        if file_type == 'compressed' and not self.options.download_compressed:
            return False
        
        # Check file size filters
        if media_item.size:
            if self.options.min_file_size > 0 and media_item.size < self.options.min_file_size:
                return False
            if self.options.max_file_size > 0 and media_item.size > self.options.max_file_size:
                return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Remove invalid characters from filename.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            Sanitized filename safe for all platforms
        """
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
```

**Usage Example**:
```python
# In downloader/coomer.py
from downloader.base import BaseDownloader, DownloadResult, MediaItem

class CoomerDownloader(BaseDownloader):
    def supports_url(self, url: str) -> bool:
        return any(domain in url for domain in ["coomer.su", "coomer.st"])
    
    def get_site_name(self) -> str:
        return "Coomer"
    
    def download(self, url: str) -> DownloadResult:
        # Implementation here
        pass
```

---

### 2. DownloaderFactory

**File**: `downloader/factory.py` (NEW FILE)

**Purpose**: Create appropriate downloader instance based on URL.

```python
"""
Factory for creating downloader instances based on URL.
"""
from typing import Optional, List, Type
from downloader.base import BaseDownloader, DownloadOptions


class DownloaderFactory:
    """
    Factory class for creating appropriate downloader based on URL.
    
    Usage:
        factory = DownloaderFactory()
        factory.register(CoomerDownloader)
        factory.register(EromeDownloader)
        
        downloader = factory.get_downloader(url, download_folder="/downloads")
        if downloader:
            result = downloader.download(url)
    """
    
    _downloader_classes: List[Type[BaseDownloader]] = []
    
    @classmethod
    def register(cls, downloader_class: Type[BaseDownloader]) -> Type[BaseDownloader]:
        """
        Register a downloader class. Can be used as decorator.
        
        Args:
            downloader_class: The downloader class to register
            
        Returns:
            The same class (for decorator usage)
        """
        if downloader_class not in cls._downloader_classes:
            cls._downloader_classes.append(downloader_class)
        return downloader_class
    
    @classmethod
    def get_downloader(
        cls,
        url: str,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        **kwargs
    ) -> Optional[BaseDownloader]:
        """
        Get appropriate downloader for the given URL.
        
        Args:
            url: The URL to find a downloader for
            download_folder: Path to save downloaded files
            options: Download configuration options
            **kwargs: Additional arguments passed to downloader constructor
            
        Returns:
            Appropriate downloader instance, or None if no match
        """
        for downloader_class in cls._downloader_classes:
            # Create temporary instance to check URL support
            instance = downloader_class(
                download_folder=download_folder,
                options=options,
                **kwargs
            )
            if instance.supports_url(url):
                return instance
        return None
    
    @classmethod
    def get_supported_sites(cls) -> List[str]:
        """
        Get list of all supported site names.
        
        Returns:
            List of site names from registered downloaders
        """
        sites = []
        for downloader_class in cls._downloader_classes:
            # Create minimal instance to get site name
            instance = downloader_class(download_folder="")
            sites.append(instance.get_site_name())
        return sites
```

---

### 3. DownloadQueue

**File**: `app/models/download_queue.py` (NEW FILE)

**Purpose**: Manage queue of download items with persistence.

```python
"""
Download queue management with persistence.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Callable
from enum import Enum
import json
import threading
from pathlib import Path
from datetime import datetime


class QueueItemStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueuePriority(Enum):
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class QueueItem:
    """A single item in the download queue."""
    id: str  # Unique identifier (UUID)
    url: str
    download_folder: str
    status: QueueItemStatus = QueueItemStatus.PENDING
    priority: QueuePriority = QueuePriority.NORMAL
    progress: float = 0.0  # 0.0 to 1.0
    error_message: Optional[str] = None
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'url': self.url,
            'download_folder': self.download_folder,
            'status': self.status.value,
            'priority': self.priority.value,
            'progress': self.progress,
            'error_message': self.error_message,
            'added_at': self.added_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QueueItem':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            url=data['url'],
            download_folder=data['download_folder'],
            status=QueueItemStatus(data['status']),
            priority=QueuePriority(data['priority']),
            progress=data.get('progress', 0.0),
            error_message=data.get('error_message'),
            added_at=data.get('added_at', datetime.now().isoformat()),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
        )


class DownloadQueue:
    """
    Thread-safe download queue with persistence.
    
    Features:
    - Add/remove items
    - Pause/resume items
    - Reorder items
    - Priority levels
    - Persistence to JSON file
    - Callbacks for queue changes
    """
    
    QUEUE_FILE = Path("resources/config/queue.json")
    
    def __init__(self, on_change: Optional[Callable[[], None]] = None):
        """
        Initialize the download queue.
        
        Args:
            on_change: Callback invoked when queue changes
        """
        self._items: List[QueueItem] = []
        self._lock = threading.RLock()
        self._on_change = on_change
        self._load()
    
    def _load(self) -> None:
        """Load queue from disk."""
        if self.QUEUE_FILE.exists():
            try:
                with open(self.QUEUE_FILE, 'r') as f:
                    data = json.load(f)
                self._items = [QueueItem.from_dict(item) for item in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load queue: {e}")
                self._items = []
    
    def _save(self) -> None:
        """Save queue to disk."""
        self.QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.QUEUE_FILE, 'w') as f:
            json.dump([item.to_dict() for item in self._items], f, indent=2)
    
    def _notify_change(self) -> None:
        """Notify listeners of queue change."""
        self._save()
        if self._on_change:
            self._on_change()
    
    def add(
        self,
        url: str,
        download_folder: str,
        priority: QueuePriority = QueuePriority.NORMAL
    ) -> QueueItem:
        """
        Add a URL to the queue.
        
        Args:
            url: URL to download
            download_folder: Where to save files
            priority: Download priority
            
        Returns:
            The created queue item
        """
        import uuid
        
        with self._lock:
            item = QueueItem(
                id=str(uuid.uuid4()),
                url=url,
                download_folder=download_folder,
                priority=priority,
            )
            self._items.append(item)
            self._sort()
            self._notify_change()
            return item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from the queue.
        
        Args:
            item_id: ID of item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        with self._lock:
            for i, item in enumerate(self._items):
                if item.id == item_id:
                    del self._items[i]
                    self._notify_change()
                    return True
            return False
    
    def get(self, item_id: str) -> Optional[QueueItem]:
        """Get an item by ID."""
        with self._lock:
            for item in self._items:
                if item.id == item_id:
                    return item
            return None
    
    def get_next_pending(self) -> Optional[QueueItem]:
        """Get the next pending item to download."""
        with self._lock:
            for item in self._items:
                if item.status == QueueItemStatus.PENDING:
                    return item
            return None
    
    def get_all(self) -> List[QueueItem]:
        """Get all items in the queue."""
        with self._lock:
            return list(self._items)
    
    def update_status(
        self,
        item_id: str,
        status: QueueItemStatus,
        progress: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update the status of a queue item."""
        with self._lock:
            item = self.get(item_id)
            if item:
                item.status = status
                if progress is not None:
                    item.progress = progress
                if error_message is not None:
                    item.error_message = error_message
                if status == QueueItemStatus.DOWNLOADING and not item.started_at:
                    item.started_at = datetime.now().isoformat()
                if status in (QueueItemStatus.COMPLETED, QueueItemStatus.FAILED, QueueItemStatus.CANCELLED):
                    item.completed_at = datetime.now().isoformat()
                self._notify_change()
    
    def pause(self, item_id: str) -> bool:
        """Pause a downloading item."""
        item = self.get(item_id)
        if item and item.status == QueueItemStatus.DOWNLOADING:
            self.update_status(item_id, QueueItemStatus.PAUSED)
            return True
        return False
    
    def resume(self, item_id: str) -> bool:
        """Resume a paused item."""
        item = self.get(item_id)
        if item and item.status == QueueItemStatus.PAUSED:
            self.update_status(item_id, QueueItemStatus.PENDING)
            return True
        return False
    
    def move_up(self, item_id: str) -> bool:
        """Move an item up in the queue."""
        with self._lock:
            for i, item in enumerate(self._items):
                if item.id == item_id and i > 0:
                    self._items[i], self._items[i-1] = self._items[i-1], self._items[i]
                    self._notify_change()
                    return True
            return False
    
    def move_down(self, item_id: str) -> bool:
        """Move an item down in the queue."""
        with self._lock:
            for i, item in enumerate(self._items):
                if item.id == item_id and i < len(self._items) - 1:
                    self._items[i], self._items[i+1] = self._items[i+1], self._items[i]
                    self._notify_change()
                    return True
            return False
    
    def clear_completed(self) -> int:
        """Remove all completed items. Returns count removed."""
        with self._lock:
            before = len(self._items)
            self._items = [
                item for item in self._items
                if item.status != QueueItemStatus.COMPLETED
            ]
            removed = before - len(self._items)
            if removed > 0:
                self._notify_change()
            return removed
    
    def _sort(self) -> None:
        """Sort queue by priority (high first) then by added time."""
        self._items.sort(key=lambda x: (x.priority.value, x.added_at))
    
    @property
    def pending_count(self) -> int:
        """Count of pending items."""
        return sum(1 for item in self._items if item.status == QueueItemStatus.PENDING)
    
    @property
    def active_count(self) -> int:
        """Count of currently downloading items."""
        return sum(1 for item in self._items if item.status == QueueItemStatus.DOWNLOADING)
```

---

### 4. RateLimiter

**File**: `downloader/rate_limiter.py` (NEW FILE)

**Purpose**: Throttle download bandwidth.

```python
"""
Rate limiter for bandwidth throttling.
"""
import time
import threading


class RateLimiter:
    """
    Token bucket rate limiter for bandwidth throttling.
    
    Usage:
        limiter = RateLimiter(rate_limit_kbps=500)  # 500 KB/s
        
        for chunk in response.iter_content(chunk_size=65536):
            limiter.acquire(len(chunk))
            file.write(chunk)
    """
    
    def __init__(self, rate_limit_kbps: int = 0):
        """
        Initialize the rate limiter.
        
        Args:
            rate_limit_kbps: Maximum rate in kilobytes per second. 0 = unlimited.
        """
        self.set_rate(rate_limit_kbps)
        self._lock = threading.Lock()
        self._tokens = self._rate_limit
        self._last_update = time.monotonic()
    
    def set_rate(self, rate_limit_kbps: int) -> None:
        """
        Update the rate limit.
        
        Args:
            rate_limit_kbps: New rate limit in KB/s. 0 = unlimited.
        """
        self._rate_limit = rate_limit_kbps * 1024 if rate_limit_kbps > 0 else 0
    
    def acquire(self, num_bytes: int) -> None:
        """
        Acquire permission to transfer bytes, blocking if necessary.
        
        Args:
            num_bytes: Number of bytes to transfer
        """
        if self._rate_limit <= 0:
            return  # No limit
        
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            
            # Add tokens based on elapsed time
            self._tokens += elapsed * self._rate_limit
            self._tokens = min(self._tokens, self._rate_limit)  # Cap at 1 second worth
            self._last_update = now
            
            # Wait if not enough tokens
            if num_bytes > self._tokens:
                wait_time = (num_bytes - self._tokens) / self._rate_limit
                time.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= num_bytes
```

---

### 5. AppConfig (Enhanced Configuration)

**File**: `app/models/config.py` (NEW FILE)

**Purpose**: Centralized configuration with validation and persistence.

```python
"""
Application configuration management.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json
from pathlib import Path


@dataclass
class NetworkConfig:
    """Network-related settings."""
    proxy_enabled: bool = False
    proxy_type: str = "http"  # http, socks4, socks5
    proxy_host: str = ""
    proxy_port: int = 8080
    proxy_username: str = ""
    proxy_password: str = ""
    bandwidth_limit_kbps: int = 0  # 0 = unlimited
    connection_timeout: int = 30
    read_timeout: int = 60


@dataclass
class DownloadConfig:
    """Download-related settings."""
    max_concurrent_downloads: int = 3
    max_retries: int = 3
    retry_interval: float = 2.0
    chunk_size: int = 1048576  # 1MB
    folder_structure: str = "default"  # default, post_number
    file_naming_mode: int = 0  # 0-3
    download_images: bool = True
    download_videos: bool = True
    download_documents: bool = True
    download_compressed: bool = True
    min_file_size_mb: float = 0.0
    max_file_size_mb: float = 0.0  # 0 = no limit
    
    def __post_init__(self):
        """Validate configuration values."""
        self.max_concurrent_downloads = max(1, min(10, self.max_concurrent_downloads))
        self.max_retries = max(0, self.max_retries)
        self.retry_interval = max(0.1, self.retry_interval)
        self.file_naming_mode = max(0, min(3, self.file_naming_mode))


@dataclass  
class UIConfig:
    """UI-related settings."""
    theme: str = "System"  # Light, Dark, System
    language: str = "en"
    window_width: int = 1000
    window_height: int = 600
    autoscroll_logs: bool = False
    show_notifications: bool = True
    minimize_to_tray: bool = False


@dataclass
class AppConfig:
    """
    Main application configuration.
    
    Usage:
        config = AppConfig.load()
        config.download.max_concurrent_downloads = 5
        config.save()
    """
    
    network: NetworkConfig = field(default_factory=NetworkConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    CONFIG_PATH = Path("resources/config/settings.json")
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load configuration from file.
        
        Returns:
            Loaded configuration, or defaults if file doesn't exist
        """
        if cls.CONFIG_PATH.exists():
            try:
                with open(cls.CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls._from_dict(data)
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                print(f"Warning: Could not load config: {e}")
        return cls()
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create config from dictionary, handling nested structures."""
        network = NetworkConfig(**data.get('network', {}))
        download = DownloadConfig(**data.get('download', {}))
        ui = UIConfig(**data.get('ui', {}))
        return cls(network=network, download=download, ui=ui)
    
    def save(self) -> None:
        """Save configuration to file."""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'network': asdict(self.network),
            'download': asdict(self.download),
            'ui': asdict(self.ui),
        }
        with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    
    def get_proxies(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for requests library.
        
        Returns:
            Proxy dict for requests, or None if disabled
        """
        if not self.network.proxy_enabled or not self.network.proxy_host:
            return None
        
        auth = ""
        if self.network.proxy_username:
            auth = f"{self.network.proxy_username}:{self.network.proxy_password}@"
        
        proxy_url = f"{self.network.proxy_type}://{auth}{self.network.proxy_host}:{self.network.proxy_port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url,
        }
```

---

## New Functions

### 1. URL Validation and Parsing

**File**: `app/utils/url_utils.py` (NEW FILE)

```python
"""
URL validation and parsing utilities.
"""
import re
from typing import List, Tuple, Optional
from urllib.parse import urlparse


# Supported site patterns
SITE_PATTERNS = {
    'coomer': re.compile(r'https?://(?:www\.)?coomer\.(su|st)/'),
    'kemono': re.compile(r'https?://(?:www\.)?kemono\.(su|cr)/'),
    'erome': re.compile(r'https?://(?:www\.)?erome\.com/'),
    'bunkr': re.compile(r'https?://(?:www\.)?bunkr[r-]?albums?\.io/'),
    'simpcity': re.compile(r'https?://(?:www\.)?simpcity\.su/'),
    'jpg5': re.compile(r'https?://(?:www\.)?jpg5\.su/'),
}


def validate_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate a URL and identify which site it belongs to.
    
    Args:
        url: The URL to validate
        
    Returns:
        Tuple of (is_valid, site_name, error_message)
        - is_valid: True if URL is valid and supported
        - site_name: Name of the site (e.g., 'coomer', 'erome') or None
        - error_message: Error description if invalid, None otherwise
    """
    url = url.strip()
    
    if not url:
        return False, None, "URL is empty"
    
    # Check basic URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, None, "Invalid URL format"
        if parsed.scheme not in ('http', 'https'):
            return False, None, "URL must use http or https"
    except Exception:
        return False, None, "Could not parse URL"
    
    # Check against supported sites
    for site_name, pattern in SITE_PATTERNS.items():
        if pattern.match(url):
            return True, site_name, None
    
    return False, None, "URL is not from a supported site"


def parse_urls(text: str) -> List[Tuple[str, bool, Optional[str]]]:
    """
    Parse multiple URLs from text (one per line).
    
    Args:
        text: Multi-line text containing URLs
        
    Returns:
        List of tuples (url, is_valid, error_message)
    """
    results = []
    seen = set()
    
    for line in text.strip().split('\n'):
        url = line.strip()
        if not url:
            continue
        
        # Check for duplicates
        if url in seen:
            results.append((url, False, "Duplicate URL"))
            continue
        seen.add(url)
        
        # Validate
        is_valid, site_name, error = validate_url(url)
        results.append((url, is_valid, error))
    
    return results


def extract_user_info(url: str) -> Optional[Tuple[str, str, str]]:
    """
    Extract site, service, and user ID from a profile URL.
    
    Args:
        url: Profile URL (e.g., https://coomer.su/onlyfans/user/username)
        
    Returns:
        Tuple of (site, service, user_id) or None if not a profile URL
    """
    # Coomer/Kemono pattern: /service/user/username
    match = re.search(r'(coomer|kemono)\.(su|st|cr)/(\w+)/user/([^/?#]+)', url)
    if match:
        site = match.group(1)
        service = match.group(3)
        user_id = match.group(4)
        return (site, service, user_id)
    
    return None


def get_base_url(url: str) -> str:
    """
    Extract base URL (scheme + netloc) from a URL.
    
    Args:
        url: Full URL
        
    Returns:
        Base URL (e.g., "https://example.com")
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
```

---

### 2. File Naming Utilities

**File**: `app/utils/file_utils.py` (NEW FILE)

```python
"""
File naming and path utilities.
"""
import re
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


# Invalid filename characters for all platforms
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# Maximum filename length (conservative for all platforms)
MAX_FILENAME_LENGTH = 200


def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        filename: The filename to sanitize
        replacement: Character to replace invalid chars with
        
    Returns:
        Sanitized filename safe for all platforms
    """
    # Replace invalid characters
    sanitized = INVALID_CHARS.sub(replacement, filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure not empty
    if not sanitized:
        sanitized = 'unnamed'
    
    # Truncate if too long (preserve extension)
    if len(sanitized) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(sanitized)
        max_name_len = MAX_FILENAME_LENGTH - len(ext)
        sanitized = name[:max_name_len] + ext
    
    return sanitized


def generate_filename(
    original_name: str,
    mode: int = 0,
    post_id: Optional[str] = None,
    user_id: Optional[str] = None,
    index: Optional[int] = None,
    timestamp: Optional[datetime] = None
) -> str:
    """
    Generate filename based on naming mode.
    
    Args:
        original_name: Original filename from server
        mode: Naming mode (0-3)
            0: Original filename
            1: post_id_original
            2: user_id_post_id_original
            3: timestamp_original
        post_id: Post identifier
        user_id: User identifier
        index: File index within post
        timestamp: Timestamp for mode 3
        
    Returns:
        Generated filename
    """
    name, ext = os.path.splitext(original_name)
    
    if mode == 0:
        result = original_name
    elif mode == 1 and post_id:
        result = f"{post_id}_{original_name}"
    elif mode == 2 and user_id and post_id:
        result = f"{user_id}_{post_id}_{original_name}"
    elif mode == 3:
        ts = timestamp or datetime.now()
        ts_str = ts.strftime("%Y%m%d_%H%M%S")
        if index is not None:
            result = f"{ts_str}_{index:04d}{ext}"
        else:
            result = f"{ts_str}_{name}{ext}"
    else:
        result = original_name
    
    return sanitize_filename(result)


def ensure_unique_path(path: Path) -> Path:
    """
    Ensure path is unique by adding number suffix if needed.
    
    Args:
        path: Desired file path
        
    Returns:
        Unique path (original or with suffix)
    """
    if not path.exists():
        return path
    
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def get_folder_structure_path(
    base_folder: str,
    structure: str,
    site: str,
    service: Optional[str] = None,
    user_id: Optional[str] = None,
    post_id: Optional[str] = None
) -> Path:
    """
    Generate folder path based on structure setting.
    
    Args:
        base_folder: Base download folder
        structure: Structure mode ('default', 'post_number', 'flat')
        site: Site name (coomer, kemono, etc.)
        service: Service name (onlyfans, patreon, etc.)
        user_id: User identifier
        post_id: Post identifier
        
    Returns:
        Path object for the download folder
    """
    base = Path(base_folder)
    
    if structure == 'flat':
        return base
    
    if structure == 'post_number' and post_id:
        if service and user_id:
            return base / site / service / user_id / post_id
        elif user_id:
            return base / site / user_id / post_id
        else:
            return base / site / post_id
    
    # Default structure
    if service and user_id:
        return base / site / service / user_id
    elif user_id:
        return base / site / user_id
    else:
        return base / site
```

---

## New Modules

### 1. UI Module Structure

**Directory**: `app/window/` (NEW DIRECTORY)

Create the following module structure:

```
app/window/
├── __init__.py
├── main_window.py      # Main application window
├── menu_bar.py         # Custom menu bar component
├── input_panel.py      # URL input and folder selection
├── options_panel.py    # Download options checkboxes
├── action_panel.py     # Download/Cancel buttons
├── log_panel.py        # Log display with filtering
├── progress_panel.py   # Progress bars
└── status_bar.py       # Footer with stats
```

**File**: `app/window/__init__.py`
```python
"""
UI window components.
"""
from app.window.main_window import MainWindow

__all__ = ['MainWindow']
```

**File**: `app/window/input_panel.py`
```python
"""
URL input panel component.
"""
import customtkinter as ctk
from typing import Callable, Optional, List
from tkinter import filedialog


class InputPanel(ctk.CTkFrame):
    """
    Panel for URL input and folder selection.
    
    Features:
    - Multi-line URL input
    - Drag-and-drop support
    - Folder selection button
    - URL validation feedback
    """
    
    def __init__(
        self,
        parent,
        on_urls_changed: Optional[Callable[[List[str]], None]] = None,
        on_folder_changed: Optional[Callable[[str], None]] = None,
        translations: Optional[dict] = None,
        **kwargs
    ):
        """
        Initialize the input panel.
        
        Args:
            parent: Parent widget
            on_urls_changed: Callback when URLs change
            on_folder_changed: Callback when folder changes
            translations: Translation dictionary
        """
        super().__init__(parent, **kwargs)
        
        self.on_urls_changed = on_urls_changed
        self.on_folder_changed = on_folder_changed
        self.tr = translations or {}
        self._download_folder = ""
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # URL Label
        self.url_label = ctk.CTkLabel(
            self,
            text=self.tr.get("paste_urls", "Paste URLs (one per line):"),
            anchor="w"
        )
        self.url_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # URL Textbox (multi-line)
        self.url_textbox = ctk.CTkTextbox(
            self,
            height=100,
            wrap="none"
        )
        self.url_textbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.url_textbox.bind("<KeyRelease>", self._on_text_changed)
        
        # URL count label
        self.url_count_label = ctk.CTkLabel(
            self,
            text="",
            anchor="e",
            text_color="gray"
        )
        self.url_count_label.pack(fill="x", padx=10)
        
        # Folder selection frame
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(fill="x", padx=10, pady=10)
        
        self.folder_button = ctk.CTkButton(
            self.folder_frame,
            text=self.tr.get("select_folder", "📁 Select Folder"),
            command=self._select_folder,
            width=120
        )
        self.folder_button.pack(side="left")
        
        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text=self.tr.get("no_folder", "No folder selected"),
            anchor="w"
        )
        self.folder_label.pack(side="left", padx=10, fill="x", expand=True)
    
    def _on_text_changed(self, event=None):
        """Handle text change event."""
        urls = self.get_urls()
        valid_count = len([u for u in urls if u])
        
        self.url_count_label.configure(
            text=f"{valid_count} URL(s)" if valid_count > 0 else ""
        )
        
        if self.on_urls_changed:
            self.on_urls_changed(urls)
    
    def _select_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(
            title=self.tr.get("select_download_folder", "Select Download Folder")
        )
        if folder:
            self._download_folder = folder
            self.folder_label.configure(text=folder)
            if self.on_folder_changed:
                self.on_folder_changed(folder)
    
    def get_urls(self) -> List[str]:
        """
        Get list of URLs from textbox.
        
        Returns:
            List of non-empty URLs
        """
        text = self.url_textbox.get("1.0", "end-1c")
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    def get_folder(self) -> str:
        """Get selected download folder."""
        return self._download_folder
    
    def set_folder(self, folder: str):
        """Set download folder."""
        self._download_folder = folder
        self.folder_label.configure(text=folder or self.tr.get("no_folder", "No folder selected"))
    
    def clear(self):
        """Clear URL input."""
        self.url_textbox.delete("1.0", "end")
        self._on_text_changed()
```

---

## UI Components

### Queue Dialog Specification

**File**: `app/dialogs/queue_dialog.py` (NEW FILE)

```python
"""
Download queue manager dialog.
"""
import customtkinter as ctk
from typing import Optional, Callable
from app.models.download_queue import DownloadQueue, QueueItem, QueueItemStatus


class QueueDialog(ctk.CTkToplevel):
    """
    Dialog for managing the download queue.
    
    Features:
    - Display all queue items with status
    - Pause/Resume/Cancel individual items
    - Reorder items with drag or buttons
    - Clear completed items
    - Live progress updates
    """
    
    def __init__(
        self,
        parent,
        queue: DownloadQueue,
        on_item_action: Optional[Callable[[str, str], None]] = None,
        translations: Optional[dict] = None,
        **kwargs
    ):
        """
        Initialize the queue dialog.
        
        Args:
            parent: Parent window
            queue: DownloadQueue instance
            on_item_action: Callback for item actions (item_id, action)
            translations: Translation dictionary
        """
        super().__init__(parent, **kwargs)
        
        self.queue = queue
        self.on_item_action = on_item_action
        self.tr = translations or {}
        
        self.title(self.tr.get("download_queue", "Download Queue"))
        self.geometry("600x400")
        
        self._create_widgets()
        self._refresh()
        
        # Set up auto-refresh
        self._refresh_job = self.after(1000, self._auto_refresh)
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Toolbar
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.pack(fill="x", padx=10, pady=10)
        
        self.pause_all_btn = ctk.CTkButton(
            self.toolbar,
            text="⏸ Pause All",
            command=self._pause_all,
            width=100
        )
        self.pause_all_btn.pack(side="left", padx=5)
        
        self.resume_all_btn = ctk.CTkButton(
            self.toolbar,
            text="▶ Resume All",
            command=self._resume_all,
            width=100
        )
        self.resume_all_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            self.toolbar,
            text="🗑 Clear Completed",
            command=self._clear_completed,
            width=120
        )
        self.clear_btn.pack(side="right", padx=5)
        
        # Queue list (scrollable frame)
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.item_widgets = {}  # item_id -> widget dict
    
    def _refresh(self):
        """Refresh the queue display."""
        items = self.queue.get_all()
        
        # Remove widgets for items no longer in queue
        current_ids = {item.id for item in items}
        for item_id in list(self.item_widgets.keys()):
            if item_id not in current_ids:
                self._remove_item_widget(item_id)
        
        # Add/update widgets for queue items
        for i, item in enumerate(items):
            if item.id in self.item_widgets:
                self._update_item_widget(item)
            else:
                self._create_item_widget(item, i)
    
    def _create_item_widget(self, item: QueueItem, index: int):
        """Create widget for a queue item."""
        frame = ctk.CTkFrame(self.list_frame)
        frame.pack(fill="x", pady=2)
        
        # Status icon
        status_icons = {
            QueueItemStatus.PENDING: "⏳",
            QueueItemStatus.DOWNLOADING: "⬇️",
            QueueItemStatus.PAUSED: "⏸",
            QueueItemStatus.COMPLETED: "✅",
            QueueItemStatus.FAILED: "❌",
            QueueItemStatus.CANCELLED: "🚫",
        }
        
        status_label = ctk.CTkLabel(frame, text=status_icons.get(item.status, "?"), width=30)
        status_label.pack(side="left", padx=5)
        
        # URL (truncated)
        url_text = item.url[:50] + "..." if len(item.url) > 50 else item.url
        url_label = ctk.CTkLabel(frame, text=url_text, anchor="w")
        url_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(frame, width=100)
        progress_bar.set(item.progress)
        progress_bar.pack(side="left", padx=5)
        
        # Action buttons
        if item.status == QueueItemStatus.DOWNLOADING:
            btn = ctk.CTkButton(frame, text="⏸", width=30, command=lambda: self._pause_item(item.id))
        elif item.status == QueueItemStatus.PAUSED:
            btn = ctk.CTkButton(frame, text="▶", width=30, command=lambda: self._resume_item(item.id))
        elif item.status == QueueItemStatus.PENDING:
            btn = ctk.CTkButton(frame, text="✗", width=30, command=lambda: self._cancel_item(item.id))
        else:
            btn = None
        
        if btn:
            btn.pack(side="left", padx=2)
        
        # Move buttons
        up_btn = ctk.CTkButton(frame, text="▲", width=25, command=lambda: self._move_up(item.id))
        up_btn.pack(side="left", padx=2)
        
        down_btn = ctk.CTkButton(frame, text="▼", width=25, command=lambda: self._move_down(item.id))
        down_btn.pack(side="left", padx=2)
        
        self.item_widgets[item.id] = {
            'frame': frame,
            'status_label': status_label,
            'url_label': url_label,
            'progress_bar': progress_bar,
        }
    
    def _update_item_widget(self, item: QueueItem):
        """Update existing item widget."""
        widgets = self.item_widgets.get(item.id)
        if widgets:
            widgets['progress_bar'].set(item.progress)
            # Update status icon
            status_icons = {
                QueueItemStatus.PENDING: "⏳",
                QueueItemStatus.DOWNLOADING: "⬇️",
                QueueItemStatus.PAUSED: "⏸",
                QueueItemStatus.COMPLETED: "✅",
                QueueItemStatus.FAILED: "❌",
                QueueItemStatus.CANCELLED: "🚫",
            }
            widgets['status_label'].configure(text=status_icons.get(item.status, "?"))
    
    def _remove_item_widget(self, item_id: str):
        """Remove widget for an item."""
        widgets = self.item_widgets.pop(item_id, None)
        if widgets:
            widgets['frame'].destroy()
    
    def _pause_item(self, item_id: str):
        self.queue.pause(item_id)
        if self.on_item_action:
            self.on_item_action(item_id, "pause")
        self._refresh()
    
    def _resume_item(self, item_id: str):
        self.queue.resume(item_id)
        if self.on_item_action:
            self.on_item_action(item_id, "resume")
        self._refresh()
    
    def _cancel_item(self, item_id: str):
        self.queue.update_status(item_id, QueueItemStatus.CANCELLED)
        if self.on_item_action:
            self.on_item_action(item_id, "cancel")
        self._refresh()
    
    def _move_up(self, item_id: str):
        self.queue.move_up(item_id)
        self._refresh()
    
    def _move_down(self, item_id: str):
        self.queue.move_down(item_id)
        self._refresh()
    
    def _pause_all(self):
        for item in self.queue.get_all():
            if item.status == QueueItemStatus.DOWNLOADING:
                self.queue.pause(item.id)
        self._refresh()
    
    def _resume_all(self):
        for item in self.queue.get_all():
            if item.status == QueueItemStatus.PAUSED:
                self.queue.resume(item.id)
        self._refresh()
    
    def _clear_completed(self):
        self.queue.clear_completed()
        self._refresh()
    
    def _auto_refresh(self):
        """Auto-refresh every second."""
        self._refresh()
        self._refresh_job = self.after(1000, self._auto_refresh)
    
    def destroy(self):
        """Clean up when closing."""
        if hasattr(self, '_refresh_job'):
            self.after_cancel(self._refresh_job)
        super().destroy()
```

---

## Configuration Schema

### settings.json Structure

**File**: `resources/config/settings.json`

```json
{
    "network": {
        "proxy_enabled": false,
        "proxy_type": "http",
        "proxy_host": "",
        "proxy_port": 8080,
        "proxy_username": "",
        "proxy_password": "",
        "bandwidth_limit_kbps": 0,
        "connection_timeout": 30,
        "read_timeout": 60
    },
    "download": {
        "max_concurrent_downloads": 3,
        "max_retries": 3,
        "retry_interval": 2.0,
        "chunk_size": 1048576,
        "folder_structure": "default",
        "file_naming_mode": 0,
        "download_images": true,
        "download_videos": true,
        "download_documents": true,
        "download_compressed": true,
        "min_file_size_mb": 0.0,
        "max_file_size_mb": 0.0
    },
    "ui": {
        "theme": "System",
        "language": "en",
        "window_width": 1000,
        "window_height": 600,
        "autoscroll_logs": false,
        "show_notifications": true,
        "minimize_to_tray": false
    }
}
```

---

## Database Schema

### Proposed Schema Updates

**File**: `resources/config/downloads.db`

```sql
-- Existing table (preserve data, add indexes)
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_url TEXT UNIQUE,
    file_path TEXT,
    file_size INTEGER,
    user_id TEXT,
    post_id TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Performance indexes
CREATE INDEX IF NOT EXISTS idx_downloads_user ON downloads(user_id);
CREATE INDEX IF NOT EXISTS idx_downloads_post ON downloads(post_id);
CREATE INDEX IF NOT EXISTS idx_downloads_date ON downloads(downloaded_at);

-- NEW: Users table for tracking favorites
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    site TEXT NOT NULL,
    service TEXT,
    username TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE
);

-- NEW: Download sessions for statistics
CREATE TABLE IF NOT EXISTS download_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    url TEXT,
    site TEXT,
    total_files INTEGER DEFAULT 0,
    completed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    skipped_files INTEGER DEFAULT 0,
    total_bytes INTEGER DEFAULT 0
);
```

---

## API Contracts

### Downloader Callback Signatures

```python
# Log callback
def log_callback(message: str) -> None:
    """
    Called with log messages.
    
    Args:
        message: Log message string
    """
    pass

# Per-file progress callback
def progress_callback(
    downloaded_bytes: int,
    total_bytes: int,
    metadata: dict
) -> None:
    """
    Called during file download with progress.
    
    Args:
        downloaded_bytes: Bytes downloaded so far
        total_bytes: Total file size in bytes
        metadata: Additional info like filename, speed
    """
    pass

# Global progress callback
def global_progress_callback(
    completed_files: int,
    total_files: int
) -> None:
    """
    Called when file counts change.
    
    Args:
        completed_files: Number of files completed
        total_files: Total number of files
    """
    pass
```

---

## Implementation Checklist

Use this checklist when implementing new features:

### Before Starting
- [ ] Read the full specification for the component
- [ ] Verify file paths match existing structure
- [ ] Check for any dependencies on other components

### During Implementation
- [ ] Follow existing code patterns in the repository
- [ ] Add type hints to all functions
- [ ] Add docstrings to all public methods
- [ ] Handle edge cases (empty inputs, invalid data)
- [ ] Use the translation system for user-facing strings

### After Implementation
- [ ] Test the component in isolation
- [ ] Test integration with existing code
- [ ] Update any related documentation
- [ ] Check for linting errors

---

*Last updated: December 2024*
