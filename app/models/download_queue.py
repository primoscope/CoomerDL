"""
Download queue management with persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Callable
from enum import Enum
import json
import threading
from pathlib import Path
from datetime import datetime
import uuid


class QueueItemStatus(Enum):
    """Status of a queue item."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueuePriority(Enum):
    """Priority level for queue items."""
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
    
    def __init__(self, on_change: Optional[Callable[[], None]] = None, persist_file: Optional[str] = None):
        """
        Initialize the download queue.
        
        Args:
            on_change: Callback invoked when queue changes
            persist_file: Path to the persistence file (default: resources/config/queue.json)
        """
        self._items: List[QueueItem] = []
        self._lock = threading.RLock()
        self._on_change = on_change
        self.QUEUE_FILE = Path(persist_file) if persist_file else self.QUEUE_FILE
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
    
    def _sort(self) -> None:
        """Sort items by priority (high first) and then by added date."""
        self._items.sort(key=lambda x: (x.priority.value, x.added_at))
    
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

    def add_batch(
        self,
        items: List[dict]
    ) -> List[QueueItem]:
        """
        Add multiple URLs to the queue in a batch.

        Args:
            items: List of dictionaries containing 'url', 'download_folder', and optionally 'priority'

        Returns:
            List of created queue items
        """
        with self._lock:
            new_items = []
            for item_data in items:
                item = QueueItem(
                    id=str(uuid.uuid4()),
                    url=item_data['url'],
                    download_folder=item_data['download_folder'],
                    priority=item_data.get('priority', QueuePriority.NORMAL),
                )
                self._items.append(item)
                new_items.append(item)

            self._sort()
            self._notify_change()
            return new_items
    
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
                if item.status not in (QueueItemStatus.COMPLETED, QueueItemStatus.CANCELLED)
            ]
            after = len(self._items)
            if before != after:
                self._notify_change()
            return before - after
    
    def get_stats(self) -> dict:
        """Get statistics about the queue."""
        with self._lock:
            stats = {
                'total': len(self._items),
                'pending': sum(1 for i in self._items if i.status == QueueItemStatus.PENDING),
                'downloading': sum(1 for i in self._items if i.status == QueueItemStatus.DOWNLOADING),
                'paused': sum(1 for i in self._items if i.status == QueueItemStatus.PAUSED),
                'completed': sum(1 for i in self._items if i.status == QueueItemStatus.COMPLETED),
                'failed': sum(1 for i in self._items if i.status == QueueItemStatus.FAILED),
                'cancelled': sum(1 for i in self._items if i.status == QueueItemStatus.CANCELLED),
            }
            return stats
