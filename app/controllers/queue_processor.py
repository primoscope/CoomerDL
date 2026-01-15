import threading
import time
import logging
from typing import Optional

from app.models.download_queue import DownloadQueue, QueueItem, QueueItemStatus
from downloader.factory import DownloaderFactory
from downloader.base import DownloadResult

logger = logging.getLogger(__name__)

class QueueProcessor:
    def __init__(self, queue: DownloadQueue, app=None):
        self.queue = queue
        self.app = app  # Reference to main app for legacy downloader access
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self.running:
            return
        self.running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("Queue processor started")

    def stop(self):
        self.running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Queue processor stopped")

    def _process_loop(self):
        while self.running and not self._stop_event.is_set():
            item = self.queue.get_next_pending()
            if item:
                self._process_item(item)
            else:
                # Wait before checking again
                time.sleep(1.0)

    def _process_item(self, item: QueueItem):
        logger.info(f"Processing queue item: {item.url}")
        self.queue.update_status(item.id, QueueItemStatus.DOWNLOADING)

        try:
            # Try factory first
            downloader = DownloaderFactory.get_downloader(
                item.url,
                download_folder=item.download_folder
            )

            if downloader:
                # Use new architecture
                result = downloader.download(item.url)
                if result.success:
                    self.queue.update_status(item.id, QueueItemStatus.COMPLETED)
                else:
                    self.queue.update_status(item.id, QueueItemStatus.FAILED, error_message=result.error_message)
            else:
                # Fallback to legacy downloader (Coomer/Kemono)
                # This is a hack until we refactor Coomer/Kemono to new architecture
                if self.app and self.app.default_downloader:
                    # We need to parse the URL to call download_single_post or similar
                    # For now, let's just mark as failed with "Not supported yet"
                    # unless we can figure out how to use the legacy downloader easily.
                    self.queue.update_status(item.id, QueueItemStatus.FAILED, error_message="URL not supported by new engine (Legacy support pending)")
                else:
                    self.queue.update_status(item.id, QueueItemStatus.FAILED, error_message="No downloader found for URL")

        except Exception as e:
            logger.error(f"Error processing item {item.id}: {e}")
            self.queue.update_status(item.id, QueueItemStatus.FAILED, error_message=str(e))
