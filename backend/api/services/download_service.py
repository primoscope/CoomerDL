"""
Download service that wraps existing downloader functionality.
Provides async interface for the FastAPI backend.
"""
import asyncio
import uuid
import logging
from typing import Optional, Dict, Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from downloader.factory import DownloaderFactory
from downloader.base import DownloadOptions as DownloaderOptions, DownloadResult
from backend.api.models.schemas import DownloadOptionsSchema, DownloadStatus

logger = logging.getLogger(__name__)

# Thread pool for running blocking downloaders
executor = ThreadPoolExecutor(max_workers=10)

# In-memory storage for active downloads (replace with Redis in production)
active_downloads: Dict[str, dict] = {}


class DownloadService:
    """Service for managing downloads."""
    
    @staticmethod
    def _convert_options(schema: Optional[DownloadOptionsSchema]) -> DownloaderOptions:
        """Convert API schema to downloader options."""
        if not schema:
            return DownloaderOptions()
        
        return DownloaderOptions(
            download_images=schema.download_images,
            download_videos=schema.download_videos,
            download_compressed=schema.download_compressed,
            download_documents=schema.download_documents,
            max_retries=schema.max_retries,
            retry_interval=schema.retry_interval,
            chunk_size=schema.chunk_size,
            timeout=schema.timeout,
            min_file_size=schema.min_file_size,
            max_file_size=schema.max_file_size,
            date_from=schema.date_from,
            date_to=schema.date_to,
            excluded_extensions=set(schema.excluded_extensions) if schema.excluded_extensions else set(),
            proxy_type=schema.proxy_type,
            proxy_url=schema.proxy_url,
            user_agent=schema.user_agent,
            bandwidth_limit_kbps=schema.bandwidth_limit_kbps,
            connection_timeout=schema.connection_timeout,
            read_timeout=schema.read_timeout,
        )
    
    @staticmethod
    async def start_download(
        url: str,
        download_folder: str,
        options: Optional[DownloadOptionsSchema] = None,
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None,
    ) -> str:
        """
        Start a download asynchronously.
        
        Args:
            url: URL to download
            download_folder: Folder to save files
            options: Download options
            progress_callback: Callback for progress updates
            log_callback: Callback for log messages
            
        Returns:
            Task ID for tracking the download
        """
        task_id = str(uuid.uuid4())
        
        # Store initial download state
        active_downloads[task_id] = {
            "task_id": task_id,
            "url": url,
            "status": DownloadStatus.PENDING,
            "progress": 0.0,
            "current_file": None,
            "total_files": 0,
            "completed_files": 0,
            "failed_files": 0,
            "download_speed": 0.0,
            "eta_seconds": None,
            "error_message": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # Convert options
        downloader_options = DownloadService._convert_options(options)
        
        # Create downloader
        downloader = DownloaderFactory.get_downloader(
            url=url,
            download_folder=download_folder,
            options=downloader_options,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )
        
        if not downloader:
            active_downloads[task_id]["status"] = DownloadStatus.FAILED
            active_downloads[task_id]["error_message"] = "No suitable downloader found for URL"
            logger.error(f"No downloader found for URL: {url}")
            return task_id
        
        # Start download in background thread
        loop = asyncio.get_event_loop()
        
        def _download_wrapper():
            """Wrapper to run download and update state."""
            try:
                logger.info(f"Starting download: {url} (task_id: {task_id})")
                active_downloads[task_id]["status"] = DownloadStatus.DOWNLOADING
                
                # Run the download (blocking call)
                result: DownloadResult = downloader.download(url)
                
                # Update final state
                if result.success:
                    active_downloads[task_id]["status"] = DownloadStatus.COMPLETED
                    logger.info(f"Download completed: {task_id}")
                else:
                    active_downloads[task_id]["status"] = DownloadStatus.FAILED
                    active_downloads[task_id]["error_message"] = result.error_message
                    logger.error(f"Download failed: {task_id} - {result.error_message}")
                
                active_downloads[task_id]["total_files"] = result.total_files
                active_downloads[task_id]["completed_files"] = result.completed_files
                active_downloads[task_id]["failed_files"] = result.failed_files
                active_downloads[task_id]["progress"] = 100.0 if result.success else active_downloads[task_id].get("progress", 0.0)
                
            except Exception as e:
                logger.exception(f"Error during download {task_id}: {e}")
                active_downloads[task_id]["status"] = DownloadStatus.FAILED
                active_downloads[task_id]["error_message"] = str(e)
            finally:
                active_downloads[task_id]["updated_at"] = datetime.utcnow()
        
        # Submit to thread pool
        loop.run_in_executor(executor, _download_wrapper)
        
        return task_id
    
    @staticmethod
    def get_download_status(task_id: str) -> Optional[dict]:
        """Get status of a download."""
        return active_downloads.get(task_id)
    
    @staticmethod
    def cancel_download(task_id: str) -> bool:
        """
        Cancel a download.
        
        Note: This requires cooperation from the downloader.
        Current implementation just updates status.
        """
        if task_id in active_downloads:
            active_downloads[task_id]["status"] = DownloadStatus.CANCELLED
            active_downloads[task_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Download cancelled: {task_id}")
            return True
        return False
    
    @staticmethod
    def get_all_downloads() -> Dict[str, dict]:
        """Get all active downloads."""
        return active_downloads
    
    @staticmethod
    def cleanup_old_downloads(max_age_hours: int = 24):
        """Clean up old completed/failed downloads from memory."""
        now = datetime.utcnow()
        to_remove = []
        
        for task_id, download in active_downloads.items():
            age = (now - download["updated_at"]).total_seconds() / 3600
            if age > max_age_hours and download["status"] in [
                DownloadStatus.COMPLETED,
                DownloadStatus.FAILED,
                DownloadStatus.CANCELLED
            ]:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del active_downloads[task_id]
            logger.debug(f"Cleaned up old download: {task_id}")
