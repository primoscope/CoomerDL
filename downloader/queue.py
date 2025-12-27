"""
Download Queue Manager - Unified job queue for all download engines.

Provides a single queue that works with all downloaders (native + yt-dlp + generic),
emits consistent events, and persists history.
"""
import threading
import queue
import logging
from typing import Optional, Callable, Dict, Any, List
from dataclasses import asdict

from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.factory import DownloaderFactory
from downloader.models import (
    DownloadJob, DownloadEvent, JobStatus, DownloadEventType,
    job_added_event, job_started_event, job_progress_event,
    item_progress_event, job_done_event, job_error_event,
    job_cancelled_event, log_event
)
from downloader.history import DownloadHistoryDB

logger = logging.getLogger(__name__)


class DownloadQueueManager:
    """
    Unified queue manager for all download operations.
    
    Features:
    - Single queue for all engines (native, yt-dlp, generic)
    - Consistent event emission for UI updates
    - Persistent history via SQLite
    - Cancellation support
    - Thread-safe operation
    
    Usage:
        def on_event(event):
            print(f"Event: {event.type.value}")
        
        manager = DownloadQueueManager(
            download_folder="/downloads",
            event_callback=on_event
        )
        
        job_id = manager.add_job("https://example.com/video")
        manager.start()
        # ... jobs are processed
        manager.stop()
    """
    
    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        event_callback: Optional[Callable[[DownloadEvent], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        history_db: Optional[DownloadHistoryDB] = None,
        max_workers: int = 1,
        use_ytdlp_fallback: bool = True,
        use_generic_fallback: bool = True,
        use_gallery_fallback: bool = True,
        ytdlp_options: Any = None,
        gallery_options: Any = None
    ):
        """
        Initialize the queue manager.
        
        Args:
            download_folder: Default folder for downloads.
            options: Default download options.
            event_callback: Function called for each event.
            log_callback: Function called for log messages.
            history_db: Database for persistence (created if None).
            max_workers: Number of concurrent download workers.
            use_ytdlp_fallback: Whether to use yt-dlp for unsupported URLs.
            use_generic_fallback: Whether to use generic downloader as last resort.
            use_gallery_fallback: Whether to use gallery-dl for image galleries.
            ytdlp_options: Options for yt-dlp downloads.
            gallery_options: Options for gallery-dl downloads.
        """
        self.download_folder = download_folder
        self.options = options or DownloadOptions()
        self.event_callback = event_callback
        self.log_callback = log_callback
        self.history_db = history_db or DownloadHistoryDB()
        self.max_workers = max_workers
        self.use_ytdlp_fallback = use_ytdlp_fallback
        self.use_generic_fallback = use_generic_fallback
        self.use_gallery_fallback = use_gallery_fallback
        self.ytdlp_options = ytdlp_options
        self.gallery_options = gallery_options
        
        # Job tracking
        self._jobs: Dict[str, DownloadJob] = {}
        self._job_queue: queue.Queue = queue.Queue()
        self._active_downloaders: Dict[str, BaseDownloader] = {}
        
        # Thread management
        self._workers: List[threading.Thread] = []
        self._running = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
    
    def add_job(
        self,
        url: str,
        options: Optional[DownloadOptions] = None,
        output_folder: Optional[str] = None
    ) -> str:
        """
        Add a new download job to the queue.
        
        Args:
            url: URL to download.
            options: Job-specific options (uses defaults if None).
            output_folder: Job-specific output folder (uses default if None).
            
        Returns:
            Job ID.
        """
        # Determine the engine that will handle this URL
        downloader = DownloaderFactory.get_downloader(
            url=url,
            download_folder=output_folder or self.download_folder,
            options=options or self.options,
            use_ytdlp_fallback=self.use_ytdlp_fallback,
            use_generic_fallback=self.use_generic_fallback,
            use_gallery_fallback=self.use_gallery_fallback,
            ytdlp_options=self.ytdlp_options,
            gallery_options=self.gallery_options
        )
        
        engine_name = downloader.get_site_name() if downloader else "Unknown"
        
        # Serialize options to JSON-compatible dict
        options_dict = self._serialize_options(options or self.options)
        
        # Create job
        job = DownloadJob.create(
            url=url,
            engine=engine_name,
            output_folder=output_folder or self.download_folder,
            options=options_dict
        )
        
        with self._lock:
            self._jobs[job.id] = job
        
        # Persist and emit event
        self.history_db.save_job(job)
        self._emit_event(job_added_event(job))
        
        # Add to queue
        self._job_queue.put(job.id)
        
        self._log(f"Job added: {job.id} for {url} (engine: {engine_name})")
        
        return job.id
    
    def _serialize_options(self, options: DownloadOptions) -> Dict[str, Any]:
        """
        Serialize DownloadOptions to a JSON-compatible dictionary.
        
        Handles special types like sets that aren't JSON-serializable.
        """
        data = asdict(options)
        # Convert sets to lists for JSON serialization
        for key, value in data.items():
            if isinstance(value, set):
                data[key] = list(value)
        return data
    
    def _deserialize_options(self, options_dict: Dict[str, Any]) -> DownloadOptions:
        """
        Deserialize a dictionary back to DownloadOptions.
        
        Handles converting lists back to sets where needed.
        """
        data = options_dict.copy()
        # Convert excluded_extensions list back to set
        if 'excluded_extensions' in data and isinstance(data['excluded_extensions'], list):
            data['excluded_extensions'] = set(data['excluded_extensions'])
        return DownloadOptions(**data)
    
    def start(self) -> None:
        """Start the queue workers."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"DownloadWorker-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)
        
        self._log(f"Queue started with {self.max_workers} worker(s)")
    
    def stop(self, cancel_pending: bool = True) -> None:
        """
        Stop the queue workers.
        
        Args:
            cancel_pending: If True, cancel all pending jobs.
        """
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        # Cancel pending jobs if requested
        if cancel_pending:
            with self._lock:
                for job_id, job in self._jobs.items():
                    if job.status == JobStatus.PENDING:
                        job.mark_cancelled()
                        self.history_db.save_job(job)
                        self._emit_event(job_cancelled_event(job))
        
        # Cancel active downloads
        with self._lock:
            for job_id, downloader in self._active_downloaders.items():
                downloader.request_cancel()
        
        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=5.0)
        
        self._workers.clear()
        self._log("Queue stopped")
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a specific job.
        
        Args:
            job_id: ID of the job to cancel.
            
        Returns:
            True if job was cancelled, False if not found or already finished.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return False
            
            # If job is running, cancel the downloader
            if job_id in self._active_downloaders:
                self._active_downloaders[job_id].request_cancel()
            else:
                # Job is pending, mark as cancelled
                job.mark_cancelled()
                self.history_db.save_job(job)
                self._emit_event(job_cancelled_event(job))
            
            return True
    
    def get_job(self, job_id: str) -> Optional[DownloadJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID to look up.
            
        Returns:
            DownloadJob if found, None otherwise.
        """
        with self._lock:
            return self._jobs.get(job_id)
    
    def list_jobs(self, status: Optional[JobStatus] = None) -> List[DownloadJob]:
        """
        List all jobs, optionally filtered by status.
        
        Args:
            status: Filter by status (optional).
            
        Returns:
            List of jobs.
        """
        with self._lock:
            jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return jobs
    
    def get_queue_size(self) -> int:
        """Get number of pending jobs in queue."""
        return self._job_queue.qsize()
    
    def is_running(self) -> bool:
        """Check if queue is running."""
        return self._running
    
    def _worker_loop(self) -> None:
        """Worker thread main loop."""
        while not self._stop_event.is_set():
            try:
                # Get next job ID with timeout
                try:
                    job_id = self._job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Check if we should stop
                if self._stop_event.is_set():
                    self._job_queue.put(job_id)  # Put back for later
                    break
                
                # Get job
                with self._lock:
                    job = self._jobs.get(job_id)
                
                if not job or job.status == JobStatus.CANCELLED:
                    continue
                
                # Process job
                self._process_job(job)
                
            except Exception as e:
                logger.exception(f"Worker error: {e}")
    
    def _process_job(self, job: DownloadJob) -> None:
        """Process a single download job."""
        # Mark job as started
        job.mark_started()
        self.history_db.save_job(job)
        self._emit_event(job_started_event(job))
        
        try:
            # Deserialize options, converting lists back to sets where needed
            job_options = self._deserialize_options(job.options_snapshot) if job.options_snapshot else self.options
            
            # Get downloader
            downloader = DownloaderFactory.get_downloader(
                url=job.url,
                download_folder=job.output_folder,
                options=job_options,
                use_ytdlp_fallback=self.use_ytdlp_fallback,
                use_generic_fallback=self.use_generic_fallback,
                use_gallery_fallback=self.use_gallery_fallback,
                ytdlp_options=self.ytdlp_options,
                gallery_options=self.gallery_options,
                log_callback=lambda msg: self._on_downloader_log(job.id, msg),
                progress_callback=lambda d, t, meta: self._on_downloader_progress(job.id, d, t, meta),
                global_progress_callback=lambda c, t: self._on_downloader_global_progress(job, c, t)
            )
            
            if not downloader:
                raise ValueError(f"No downloader available for URL: {job.url}")
            
            # Track active downloader for cancellation
            with self._lock:
                self._active_downloaders[job.id] = downloader
            
            # Run download
            result = downloader.download(job.url)
            
            # Update job from result
            job.total_items = result.total_files
            job.completed_items = result.completed_files
            job.failed_items = len(result.failed_files)
            job.skipped_items = len(result.skipped_files)
            
            # Determine final status
            if downloader.is_cancelled():
                job.mark_cancelled()
                self._emit_event(job_cancelled_event(job))
            elif result.success:
                job.mark_completed()
            else:
                job.mark_failed(result.error_message or "Download failed")
                self._emit_event(job_error_event(job, job.error_message))
            
            # Always emit JOB_DONE at the end (per tests/CONTRACTS.md)
            self._emit_event(job_done_event(job))
            
        except Exception as e:
            logger.exception(f"Job {job.id} failed: {e}")
            job.mark_failed(str(e))
            self._emit_event(job_error_event(job, str(e)))
            # Emit JOB_DONE even after error (per tests/CONTRACTS.md)
            self._emit_event(job_done_event(job))
        
        finally:
            # Remove from active downloaders
            with self._lock:
                self._active_downloaders.pop(job.id, None)
            
            # Persist final state
            self.history_db.save_job(job)
    
    def _on_downloader_log(self, job_id: str, message: str) -> None:
        """Handle log message from downloader."""
        event = log_event(job_id, message)
        self._emit_event(event)
        self.history_db.append_event(event)
    
    def _on_downloader_progress(
        self,
        job_id: str,
        downloaded: int,
        total: int,
        metadata: Dict[str, Any]
    ) -> None:
        """Handle per-file progress from downloader."""
        event = item_progress_event(
            job_id=job_id,
            downloaded_bytes=downloaded,
            total_bytes=total,
            file_id=metadata.get('file_id'),
            file_path=metadata.get('file_path') or metadata.get('filename'),
            url=metadata.get('url'),
            speed=metadata.get('speed'),
            eta=metadata.get('eta'),
            status=metadata.get('status')
        )
        self._emit_event(event)
    
    def _on_downloader_global_progress(
        self,
        job: DownloadJob,
        completed: int,
        total: int
    ) -> None:
        """Handle global progress from downloader."""
        job.completed_items = completed
        job.total_items = total
        
        event = job_progress_event(job, completed, total)
        self._emit_event(event)
    
    def _emit_event(self, event: DownloadEvent) -> None:
        """Emit an event to the callback."""
        if self.event_callback:
            try:
                self.event_callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
    
    def _log(self, message: str) -> None:
        """Log a message."""
        logger.info(message)
        if self.log_callback:
            try:
                self.log_callback(message)
            except Exception:
                pass
