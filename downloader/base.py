"""
Base downloader class that all site-specific downloaders must inherit from.
Provides standardized interface and common functionality.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from enum import Enum
import threading
import re


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
    excluded_extensions: set = field(default_factory=set)  # Set of extensions to skip, e.g. {'.webm', '.gif'}


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
        enable_widgets_callback: Optional[Callable[[bool], None]] = None,
        tr: Optional[Callable[[str], str]] = None,
        domain_limiter: Optional[Any] = None,
        retry_policy: Optional[Any] = None,
    ):
        """
        Initialize the downloader.
        
        Args:
            download_folder: Path to save downloaded files
            options: Download configuration options
            log_callback: Function to call with log messages
            progress_callback: Function to call with per-file progress (downloaded, total, metadata)
            global_progress_callback: Function to call with overall progress (completed, total)
            enable_widgets_callback: Function to enable/disable UI widgets
            tr: Translation function for internationalization
            domain_limiter: Optional DomainLimiter for rate limiting
            retry_policy: Optional RetryPolicy for retry behavior
        """
        self.download_folder = download_folder
        self.options = options or DownloadOptions()
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.global_progress_callback = global_progress_callback
        self.enable_widgets_callback = enable_widgets_callback
        self.tr = tr or (lambda x: x)  # Default to identity function if no translation
        self.domain_limiter = domain_limiter
        self.retry_policy = retry_policy
        
        # Cancellation mechanism - use Event for thread safety
        self.cancel_event = threading.Event()
        
        # Progress tracking
        self.total_files = 0
        self.completed_files = 0
        self.failed_files: List[str] = []
        self.skipped_files: List[str] = []
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Lightweight class-level check if this downloader can handle the given URL.
        
        This method should NOT require instantiation and should be fast.
        Override this in subclasses for efficient URL routing in the factory.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this downloader supports the URL, False otherwise
        """
        # Default implementation returns False; subclasses should override
        return False
    
    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """
        Check if this downloader can handle the given URL.
        
        Note: Prefer implementing can_handle() classmethod for factory routing
        to avoid expensive instantiation. This instance method is kept for
        backward compatibility.
        
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
        self.log(self.tr("Download cancellation requested."))
    
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
        """
        Report per-file download progress.
        
        Standard metadata fields (recommended for consistent event handling):
            file_id: Stable unique identifier for the file within this job
            file_path: Local path where the file is being saved
            filename: Just the filename (if file_path not known)
            url: Source URL of the file
            status: Current status string (e.g., "Downloading", "Processing")
            speed: Download speed in bytes/second
            eta: Estimated time remaining in seconds
        
        Args:
            downloaded: Bytes downloaded so far for current file.
            total: Total bytes for current file (0 if unknown).
            **kwargs: Additional metadata fields.
        """
        if self.progress_callback:
            self.progress_callback(downloaded, total, kwargs)
    
    def report_global_progress(self) -> None:
        """Report overall download progress."""
        if self.global_progress_callback:
            self.global_progress_callback(self.completed_files, self.total_files)
    
    def enable_widgets(self, enabled: bool) -> None:
        """Enable or disable UI widgets."""
        if self.enable_widgets_callback:
            self.enable_widgets_callback(enabled)
    
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
    
    def should_skip_file(self, url: str, filename: str = None, post_date: str = None) -> tuple[bool, str]:
        """
        Check if a file should be skipped based on advanced filters.
        Performs HEAD request to check file size if size filtering is enabled.
        
        Args:
            url: The file URL
            filename: Optional filename for extension checking
            post_date: Optional post date (ISO format YYYY-MM-DD) for date filtering
            
        Returns:
            Tuple of (should_skip: bool, reason: str)
        """
        # Check extension blacklist if provided
        if hasattr(self.options, 'excluded_extensions') and self.options.excluded_extensions:
            if filename:
                ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                if ext in self.options.excluded_extensions:
                    return True, f"Extension {ext} is blacklisted"
        
        # Check date range if provided
        if post_date and (self.options.date_from or self.options.date_to):
            try:
                from datetime import datetime
                post_dt = datetime.fromisoformat(post_date)
                
                if self.options.date_from:
                    date_from = datetime.fromisoformat(self.options.date_from)
                    if post_dt < date_from:
                        return True, f"Post date {post_date} is before {self.options.date_from}"
                
                if self.options.date_to:
                    date_to = datetime.fromisoformat(self.options.date_to)
                    if post_dt > date_to:
                        return True, f"Post date {post_date} is after {self.options.date_to}"
            except (ValueError, AttributeError):
                pass  # Ignore date parsing errors
        
        # Check file size if size filtering is enabled
        if self.options.min_file_size > 0 or self.options.max_file_size > 0:
            file_size = self.get_file_size_head(url)
            if file_size:
                if self.options.min_file_size > 0 and file_size < self.options.min_file_size:
                    size_mb = file_size / (1024 * 1024)
                    min_mb = self.options.min_file_size / (1024 * 1024)
                    return True, f"File size {size_mb:.2f}MB is below minimum {min_mb:.2f}MB"
                
                if self.options.max_file_size > 0 and file_size > self.options.max_file_size:
                    size_mb = file_size / (1024 * 1024)
                    max_mb = self.options.max_file_size / (1024 * 1024)
                    return True, f"File size {size_mb:.2f}MB exceeds maximum {max_mb:.2f}MB"
        
        return False, ""
    
    def get_file_size_head(self, url: str) -> Optional[int]:
        """
        Get file size using HEAD request without downloading the file.
        
        Args:
            url: The file URL
            
        Returns:
            File size in bytes, or None if cannot be determined
        """
        try:
            response = self.safe_request(url, method='HEAD')
            if response and 'Content-Length' in response.headers:
                return int(response.headers['Content-Length'])
        except (ValueError, KeyError, Exception):
            pass
        return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Remove invalid characters from filename.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            Sanitized filename safe for all platforms
        """
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    @staticmethod
    def canonicalize_url(url: str) -> str:
        """
        Canonicalize a URL for deduplication.
        
        Strips fragments, normalizes some query parameters.
        
        Args:
            url: URL to canonicalize.
            
        Returns:
            Canonical URL string.
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        try:
            parsed = urlparse(url)
            
            # Remove fragment
            parsed = parsed._replace(fragment='')
            
            # Sort query parameters for consistency
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=True)
                # Sort and flatten
                sorted_params = sorted(
                    (k, v[0] if len(v) == 1 else v)
                    for k, v in params.items()
                )
                parsed = parsed._replace(query=urlencode(sorted_params, doseq=True))
            
            return urlunparse(parsed)
        except Exception:
            return url
    
    def safe_request(self, url: str, method: str = 'GET', **kwargs):
        """
        Perform a safe HTTP request with retries, backoff, and rate limiting.
        
        Features:
        - Exponential backoff with jitter (if retry_policy is set)
        - Per-domain rate limiting (if domain_limiter is set)
        - Cancellation check between retries
        - Special handling for 429 rate limit responses
        
        Args:
            url: The URL to request
            method: HTTP method ('GET', 'HEAD', etc.)
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object, or None if request fails
        """
        import requests
        import time
        from urllib.parse import urlparse
        
        # Use retry policy if available, otherwise fall back to options
        if self.retry_policy:
            max_attempts = self.retry_policy.max_attempts
        else:
            max_attempts = self.options.max_retries
        
        timeout = kwargs.pop('timeout', self.options.timeout)
        
        # Extract domain for rate limiting
        domain = urlparse(url).netloc.lower()
        
        for attempt in range(max_attempts):
            # Check cancellation
            if self.is_cancelled():
                return None
            
            try:
                # Apply domain rate limiting if available
                if self.domain_limiter:
                    self.domain_limiter.acquire(domain)
                
                try:
                    if method.upper() == 'HEAD':
                        response = requests.head(url, timeout=timeout, **kwargs)
                    else:
                        response = requests.get(url, timeout=timeout, **kwargs)
                    
                    # Check for rate limiting
                    if response.status_code == 429:
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                wait_time = int(retry_after)
                            except ValueError:
                                wait_time = 30
                        else:
                            wait_time = self._compute_backoff(attempt)
                        
                        self.log(self.tr(f"Rate limited (429). Waiting {wait_time:.1f}s..."))
                        time.sleep(wait_time)
                        continue
                    
                    # Check for other retryable status codes
                    if self.retry_policy and self.retry_policy.is_retryable_status(response.status_code):
                        if attempt < max_attempts - 1:
                            wait_time = self._compute_backoff(attempt)
                            self.log(self.tr(f"Server error ({response.status_code}). Retrying in {wait_time:.1f}s..."))
                            time.sleep(wait_time)
                            continue
                    
                    response.raise_for_status()
                    return response
                    
                finally:
                    # Release domain slot
                    if self.domain_limiter:
                        self.domain_limiter.release(domain)
                
            except requests.exceptions.RequestException as e:
                should_retry = False
                
                if self.retry_policy:
                    should_retry = self.retry_policy.is_retryable_exception(e)
                else:
                    # Default: retry on common transient errors
                    should_retry = isinstance(e, (
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                    ))
                
                if should_retry and attempt < max_attempts - 1:
                    wait_time = self._compute_backoff(attempt)
                    self.log(self.tr(f"Request failed: {e}. Retrying in {wait_time:.1f}s..."))
                    time.sleep(wait_time)
                else:
                    self.log(self.tr(f"Request failed after {attempt + 1} attempts: {e}"))
                    return None
        
        return None
    
    def _compute_backoff(self, attempt: int) -> float:
        """
        Compute backoff delay for retry attempt.
        
        Args:
            attempt: Retry attempt number (0-indexed).
            
        Returns:
            Delay in seconds.
        """
        if self.retry_policy:
            from downloader.policies import compute_backoff
            return compute_backoff(attempt, self.retry_policy)
        else:
            # Simple exponential backoff with cap
            import random
            delay = min(self.options.retry_interval * (2 ** attempt), 30.0)
            # Add small jitter
            delay = delay * (1 + random.uniform(-0.1, 0.1))
            return delay
    
    def download_file(self, url: str, filepath: str, chunk_size: int = None) -> bool:
        """
        Download a file from URL to filepath.
        
        Args:
            url: The file URL
            filepath: Local path to save the file
            chunk_size: Chunk size for download (uses options.chunk_size if None)
            
        Returns:
            True if download successful, False otherwise
        """
        if self.is_cancelled():
            return False
        
        try:
            import os
            
            chunk_size = chunk_size or self.options.chunk_size
            
            response = self.safe_request(url, stream=True)
            if not response:
                return False
            
            # Create directory if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Download file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.is_cancelled():
                        # Delete partial file
                        try:
                            f.close()
                            os.remove(filepath)
                        except:
                            pass
                        return False
                    
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            self.log(self.tr(f"Error downloading file: {e}"))
            # Try to clean up partial file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
            return False
