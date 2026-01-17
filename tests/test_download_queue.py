"""
Unit tests for DownloadQueue.
"""
import pytest
import json
from app.models.download_queue import (
    DownloadQueue,
    QueueItem,
    QueueItemStatus,
    QueuePriority,
)


@pytest.fixture
def mock_queue_file(tmp_path, monkeypatch):
    """Mock the queue file path to use tmp_path."""
    queue_file = tmp_path / "queue.json"
    monkeypatch.setattr(
        'app.models.download_queue.DownloadQueue.QUEUE_FILE',
        queue_file
    )
    return queue_file


@pytest.fixture
def queue(mock_queue_file):
    """Create a fresh DownloadQueue for testing."""
    return DownloadQueue()


class TestDownloadQueueAddRemove:
    """Test adding and removing items from queue."""
    
    def test_add_item(self, queue):
        """Test adding an item to the queue."""
        item = queue.add(
            url="https://example.com/test",
            download_folder="/downloads"
        )
        
        assert item is not None
        assert item.id is not None
        assert item.url == "https://example.com/test"
        assert item.download_folder == "/downloads"
        assert item.status == QueueItemStatus.PENDING
        assert item.priority == QueuePriority.NORMAL
    
    def test_add_multiple_items(self, queue):
        """Test adding multiple items."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        
        all_items = queue.get_all()
        assert len(all_items) == 2
        assert item1 in all_items
        assert item2 in all_items

    def test_add_batch(self, queue):
        """Test adding multiple items in batch."""
        items = [
            {'url': "https://example.com/1", 'download_folder': "/downloads"},
            {'url': "https://example.com/2", 'download_folder': "/downloads"},
            {'url': "https://example.com/3", 'download_folder': "/downloads", 'priority': QueuePriority.HIGH},
        ]

        added_items = queue.add_batch(items)

        assert len(added_items) == 3

        all_items = queue.get_all()
        assert len(all_items) == 3

        # Verify ordering (High first)
        assert all_items[0].url == "https://example.com/3"
        assert all_items[0].priority == QueuePriority.HIGH
    
    def test_add_item_with_priority(self, queue):
        """Test adding item with custom priority."""
        item = queue.add(
            url="https://example.com/test",
            download_folder="/downloads",
            priority=QueuePriority.HIGH
        )
        
        assert item.priority == QueuePriority.HIGH
    
    def test_remove_item(self, queue):
        """Test removing an item."""
        item = queue.add("https://example.com/test", "/downloads")
        assert len(queue.get_all()) == 1
        
        result = queue.remove(item.id)
        assert result is True
        assert len(queue.get_all()) == 0
    
    def test_remove_nonexistent_item(self, queue):
        """Test removing an item that doesn't exist."""
        result = queue.remove("nonexistent-id")
        assert result is False
    
    def test_get_item_by_id(self, queue):
        """Test retrieving item by ID."""
        item = queue.add("https://example.com/test", "/downloads")
        
        retrieved = queue.get(item.id)
        assert retrieved is not None
        assert retrieved.id == item.id
        assert retrieved.url == item.url
    
    def test_get_nonexistent_item(self, queue):
        """Test getting item that doesn't exist."""
        item = queue.get("nonexistent-id")
        assert item is None
    
    def test_get_all_empty(self, queue):
        """Test getting all items when queue is empty."""
        items = queue.get_all()
        assert isinstance(items, list)
        assert len(items) == 0


class TestDownloadQueueOrdering:
    """Test queue ordering and priority."""
    
    def test_priority_ordering(self, queue):
        """Test that items are ordered by priority."""
        # Add items in reverse priority order
        low = queue.add("https://example.com/low", "/downloads", priority=QueuePriority.LOW)
        normal = queue.add("https://example.com/normal", "/downloads", priority=QueuePriority.NORMAL)
        high = queue.add("https://example.com/high", "/downloads", priority=QueuePriority.HIGH)
        
        all_items = queue.get_all()
        
        # Should be ordered: HIGH (1), NORMAL (2), LOW (3)
        assert all_items[0].id == high.id
        assert all_items[1].id == normal.id
        assert all_items[2].id == low.id
    
    def test_same_priority_ordering(self, queue):
        """Test that items with same priority are ordered by add time."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        item3 = queue.add("https://example.com/3", "/downloads")
        
        all_items = queue.get_all()
        
        # Should maintain add order for same priority
        assert all_items[0].id == item1.id
        assert all_items[1].id == item2.id
        assert all_items[2].id == item3.id
    
    def test_get_next_pending(self, queue):
        """Test getting next pending item."""
        high = queue.add("https://example.com/high", "/downloads", priority=QueuePriority.HIGH)
        queue.add("https://example.com/normal", "/downloads", priority=QueuePriority.NORMAL)
        
        next_item = queue.get_next_pending()
        
        # Should return highest priority pending item
        assert next_item is not None
        assert next_item.id == high.id
    
    def test_get_next_pending_skips_non_pending(self, queue):
        """Test that get_next_pending skips non-pending items."""
        high = queue.add("https://example.com/high", "/downloads", priority=QueuePriority.HIGH)
        normal = queue.add("https://example.com/normal", "/downloads", priority=QueuePriority.NORMAL)
        
        # Mark high priority as downloading
        queue.update_status(high.id, QueueItemStatus.DOWNLOADING)
        
        next_item = queue.get_next_pending()
        
        # Should return next pending item (normal priority)
        assert next_item is not None
        assert next_item.id == normal.id
    
    def test_get_next_pending_empty(self, queue):
        """Test getting next pending when queue is empty."""
        next_item = queue.get_next_pending()
        assert next_item is None
    
    def test_move_up(self, queue):
        """Test moving item up in queue."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        item3 = queue.add("https://example.com/3", "/downloads")
        
        result = queue.move_up(item2.id)
        assert result is True
        
        all_items = queue.get_all()
        assert all_items[0].id == item2.id
        assert all_items[1].id == item1.id
        assert all_items[2].id == item3.id
    
    def test_move_up_first_item(self, queue):
        """Test that moving up first item returns False."""
        item1 = queue.add("https://example.com/1", "/downloads")
        queue.add("https://example.com/2", "/downloads")
        
        result = queue.move_up(item1.id)
        assert result is False
    
    def test_move_down(self, queue):
        """Test moving item down in queue."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        item3 = queue.add("https://example.com/3", "/downloads")
        
        result = queue.move_down(item2.id)
        assert result is True
        
        all_items = queue.get_all()
        assert all_items[0].id == item1.id
        assert all_items[1].id == item3.id
        assert all_items[2].id == item2.id
    
    def test_move_down_last_item(self, queue):
        """Test that moving down last item returns False."""
        queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        
        result = queue.move_down(item2.id)
        assert result is False


class TestDownloadQueueStatus:
    """Test queue item status updates."""
    
    def test_update_status(self, queue):
        """Test updating item status."""
        item = queue.add("https://example.com/test", "/downloads")
        
        queue.update_status(item.id, QueueItemStatus.DOWNLOADING)
        
        updated = queue.get(item.id)
        assert updated.status == QueueItemStatus.DOWNLOADING
    
    def test_update_status_with_progress(self, queue):
        """Test updating status with progress."""
        item = queue.add("https://example.com/test", "/downloads")
        
        queue.update_status(item.id, QueueItemStatus.DOWNLOADING, progress=0.5)
        
        updated = queue.get(item.id)
        assert updated.progress == 0.5
    
    def test_update_status_with_error(self, queue):
        """Test updating status with error message."""
        item = queue.add("https://example.com/test", "/downloads")
        
        queue.update_status(
            item.id,
            QueueItemStatus.FAILED,
            error_message="Connection failed"
        )
        
        updated = queue.get(item.id)
        assert updated.status == QueueItemStatus.FAILED
        assert updated.error_message == "Connection failed"
    
    def test_pause_item(self, queue):
        """Test pausing a downloading item."""
        item = queue.add("https://example.com/test", "/downloads")
        queue.update_status(item.id, QueueItemStatus.DOWNLOADING)
        
        result = queue.pause(item.id)
        assert result is True
        
        updated = queue.get(item.id)
        assert updated.status == QueueItemStatus.PAUSED
    
    def test_pause_non_downloading_item(self, queue):
        """Test that pausing non-downloading item returns False."""
        item = queue.add("https://example.com/test", "/downloads")
        
        result = queue.pause(item.id)
        assert result is False
    
    def test_resume_item(self, queue):
        """Test resuming a paused item."""
        item = queue.add("https://example.com/test", "/downloads")
        queue.update_status(item.id, QueueItemStatus.DOWNLOADING)
        queue.pause(item.id)
        
        result = queue.resume(item.id)
        assert result is True
        
        updated = queue.get(item.id)
        assert updated.status == QueueItemStatus.PENDING
    
    def test_resume_non_paused_item(self, queue):
        """Test that resuming non-paused item returns False."""
        item = queue.add("https://example.com/test", "/downloads")
        
        result = queue.resume(item.id)
        assert result is False


class TestDownloadQueuePersistence:
    """Test queue persistence to JSON."""
    
    def test_save_queue_creates_file(self, queue, mock_queue_file):
        """Test that adding item creates queue file."""
        queue.add("https://example.com/test", "/downloads")
        
        assert mock_queue_file.exists()
    
    def test_save_queue_structure(self, queue, mock_queue_file):
        """Test that saved queue has correct JSON structure."""
        item = queue.add("https://example.com/test", "/downloads")
        
        with open(mock_queue_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['id'] == item.id
        assert data[0]['url'] == item.url
        assert data[0]['status'] == QueueItemStatus.PENDING.value
        assert data[0]['priority'] == QueuePriority.NORMAL.value
    
    def test_load_queue_from_file(self, queue, mock_queue_file):
        """Test loading queue from existing file."""
        # Create queue file manually - save in sorted order (high priority first)
        queue_data = [
            {
                'id': 'test-id-2',
                'url': 'https://example.com/2',
                'download_folder': '/downloads',
                'status': 'completed',
                'priority': 1,  # HIGH priority
                'progress': 1.0,
                'error_message': None,
                'added_at': '2024-01-01T00:01:00',
                'started_at': '2024-01-01T00:02:00',
                'completed_at': '2024-01-01T00:03:00',
            },
            {
                'id': 'test-id-1',
                'url': 'https://example.com/1',
                'download_folder': '/downloads',
                'status': 'pending',
                'priority': 2,  # NORMAL priority
                'progress': 0.0,
                'error_message': None,
                'added_at': '2024-01-01T00:00:00',
                'started_at': None,
                'completed_at': None,
            }
        ]
        
        # Write to file and reload the existing queue
        with open(mock_queue_file, 'w') as f:
            json.dump(queue_data, f)
        
        # Reload by calling internal load method
        queue._load()
        
        items = queue.get_all()
        assert len(items) == 2
        # Verify the data was loaded correctly (preserves file order)
        assert items[0].id == 'test-id-2'
        assert items[0].url == 'https://example.com/2'
        assert items[0].priority.value == 1  # HIGH priority
        assert items[0].status == QueueItemStatus.COMPLETED
        assert items[1].id == 'test-id-1'
        assert items[1].url == 'https://example.com/1'
        assert items[1].priority.value == 2  # NORMAL priority
    
    def test_queue_on_change_callback(self, queue):
        """Test that on_change callback is called."""
        callback_called = []
        
        def on_change():
            callback_called.append(True)
        
        queue._on_change = on_change
        
        queue.add("https://example.com/test", "/downloads")
        
        assert len(callback_called) == 1


class TestDownloadQueueUtilities:
    """Test queue utility methods."""
    
    def test_clear_completed(self, queue):
        """Test clearing completed items."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        item3 = queue.add("https://example.com/3", "/downloads")
        
        queue.update_status(item1.id, QueueItemStatus.COMPLETED)
        queue.update_status(item2.id, QueueItemStatus.CANCELLED)
        
        removed_count = queue.clear_completed()
        
        assert removed_count == 2
        assert len(queue.get_all()) == 1
        assert queue.get_all()[0].id == item3.id
    
    def test_get_stats(self, queue):
        """Test getting queue statistics."""
        item1 = queue.add("https://example.com/1", "/downloads")
        item2 = queue.add("https://example.com/2", "/downloads")
        item3 = queue.add("https://example.com/3", "/downloads")
        queue.add("https://example.com/4", "/downloads")
        
        queue.update_status(item1.id, QueueItemStatus.DOWNLOADING)
        queue.update_status(item2.id, QueueItemStatus.COMPLETED)
        queue.update_status(item3.id, QueueItemStatus.FAILED)
        # item4 remains PENDING
        
        stats = queue.get_stats()
        
        assert stats['total'] == 4
        assert stats['pending'] == 1
        assert stats['downloading'] == 1
        assert stats['completed'] == 1
        assert stats['failed'] == 1
        assert stats['paused'] == 0
        assert stats['cancelled'] == 0
    
    def test_get_stats_empty_queue(self, queue):
        """Test getting stats for empty queue."""
        stats = queue.get_stats()
        
        assert stats['total'] == 0
        assert stats['pending'] == 0
        assert stats['downloading'] == 0


class TestQueueItemSerialization:
    """Test QueueItem to_dict and from_dict."""
    
    def test_queue_item_to_dict(self):
        """Test converting QueueItem to dictionary."""
        item = QueueItem(
            id="test-id",
            url="https://example.com/test",
            download_folder="/downloads",
            status=QueueItemStatus.PENDING,
            priority=QueuePriority.HIGH,
        )
        
        item_dict = item.to_dict()
        
        assert item_dict['id'] == "test-id"
        assert item_dict['url'] == "https://example.com/test"
        assert item_dict['status'] == "pending"
        assert item_dict['priority'] == 1
    
    def test_queue_item_from_dict(self):
        """Test creating QueueItem from dictionary."""
        item_dict = {
            'id': 'test-id',
            'url': 'https://example.com/test',
            'download_folder': '/downloads',
            'status': 'downloading',
            'priority': 2,
            'progress': 0.5,
            'error_message': None,
            'added_at': '2024-01-01T00:00:00',
            'started_at': '2024-01-01T00:01:00',
            'completed_at': None,
        }
        
        item = QueueItem.from_dict(item_dict)
        
        assert item.id == "test-id"
        assert item.url == "https://example.com/test"
        assert item.status == QueueItemStatus.DOWNLOADING
        assert item.priority == QueuePriority.NORMAL
        assert item.progress == 0.5
