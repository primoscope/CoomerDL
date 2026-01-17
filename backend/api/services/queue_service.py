"""
Queue service that wraps the persistence queue.
"""
from typing import List, Optional
import logging
from app.models.download_queue import DownloadQueue, QueueItem, QueuePriority
from backend.api.models.schemas import DownloadOptionsSchema
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Singleton instance
_queue_instance = None

def get_queue() -> DownloadQueue:
    """Get the singleton queue instance."""
    global _queue_instance
    if _queue_instance is None:
        # Using the same path as desktop app for consistency if running locally
        _queue_instance = DownloadQueue(persist_file="resources/config/download_queue.json")
    return _queue_instance

class QueueService:
    """Service for managing the download queue."""

    @staticmethod
    def get_all_items() -> List[QueueItem]:
        """Get all items in the queue."""
        queue = get_queue()
        return queue.get_all()

    @staticmethod
    def get_next_pending() -> Optional[QueueItem]:
        """Get the next pending item."""
        queue = get_queue()
        return queue.get_next_pending()

    @staticmethod
    def add_item(
        url: str,
        options: Optional[DownloadOptionsSchema] = None,
        priority: int = 2
    ) -> QueueItem:
        """Add an item to the queue."""
        queue = get_queue()

        # Convert schema options to dict for storage
        options_dict = options.dict() if options else None

        # Map priority int to enum
        try:
            priority_enum = QueuePriority(priority)
        except ValueError:
            priority_enum = QueuePriority.NORMAL

        return queue.add(
            url=url,
            download_folder=settings.local_download_folder,
            priority=priority_enum,
            options=options_dict
        )

    @staticmethod
    def remove_item(item_id: str) -> bool:
        """Remove an item from the queue."""
        queue = get_queue()
        return queue.remove(item_id)

    @staticmethod
    def pause_item(item_id: str) -> bool:
        """Pause a queue item."""
        queue = get_queue()
        return queue.pause(item_id)

    @staticmethod
    def resume_item(item_id: str) -> bool:
        """Resume a queue item."""
        queue = get_queue()
        return queue.resume(item_id)

    @staticmethod
    def move_item_up(item_id: str) -> bool:
        """Move an item up."""
        queue = get_queue()
        return queue.move_up(item_id)

    @staticmethod
    def move_item_down(item_id: str) -> bool:
        """Move an item down."""
        queue = get_queue()
        return queue.move_down(item_id)

    @staticmethod
    def clear_completed() -> int:
        """Clear completed items."""
        queue = get_queue()
        return queue.clear_completed()
