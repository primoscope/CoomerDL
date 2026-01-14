#!/usr/bin/env python3
"""
Simple integration test for queue functionality.
Tests the basic workflow without GUI dependencies.
"""
import sys
import tempfile
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.download_queue import (
    DownloadQueue, 
    QueueItem, 
    QueueItemStatus, 
    QueuePriority
)


def test_queue_basic_workflow():
    """Test basic queue operations."""
    print("Testing basic queue workflow...")
    
    # Create a temporary queue file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
    
    try:
        # Initialize queue
        queue = DownloadQueue(persist_file=queue_file)
        
        # Test 1: Add items to queue
        print("✓ Test 1: Adding URLs to queue...")
        urls = [
            "https://example.com/video1",
            "https://example.com/video2",
            "https://example.com/video3"
        ]
        
        for url in urls:
            item = queue.add(url, "/downloads", priority=QueuePriority.NORMAL)
            assert item is not None, "Failed to add item to queue"
            assert item.status == QueueItemStatus.PENDING, "Item should be pending"
        
        print(f"  Added {len(urls)} URLs to queue")
        
        # Test 2: Get queue stats
        print("✓ Test 2: Getting queue stats...")
        stats = queue.get_stats()
        assert stats['total'] == 3, f"Expected 3 total items, got {stats['total']}"
        assert stats['pending'] == 3, f"Expected 3 pending items, got {stats['pending']}"
        print(f"  Stats: {stats}")
        
        # Test 3: Get next pending item
        print("✓ Test 3: Getting next pending item...")
        next_item = queue.get_next_pending()
        assert next_item is not None, "Should have a pending item"
        assert next_item.url in urls, "Item URL should be from our list"
        print(f"  Next item: {next_item.url}")
        
        # Test 4: Update item status to downloading
        print("✓ Test 4: Updating item status...")
        queue.update_status(next_item.id, QueueItemStatus.DOWNLOADING, progress=0.5)
        stats = queue.get_stats()
        assert stats['downloading'] == 1, "Should have 1 downloading item"
        assert stats['pending'] == 2, "Should have 2 pending items"
        print(f"  Updated stats: {stats}")
        
        # Test 5: Complete item
        print("✓ Test 5: Completing item...")
        queue.update_status(next_item.id, QueueItemStatus.COMPLETED, progress=1.0)
        stats = queue.get_stats()
        assert stats['completed'] == 1, "Should have 1 completed item"
        assert stats['downloading'] == 0, "Should have 0 downloading items"
        print(f"  Completed stats: {stats}")
        
        # Test 6: Clear completed items
        print("✓ Test 6: Clearing completed items...")
        removed = queue.clear_completed()
        assert removed == 1, f"Should have removed 1 item, removed {removed}"
        stats = queue.get_stats()
        assert stats['total'] == 2, f"Should have 2 items left, got {stats['total']}"
        print(f"  Removed {removed} completed item(s)")
        
        # Test 7: Persistence
        print("✓ Test 7: Testing persistence...")
        # Create a new queue instance with same file
        queue2 = DownloadQueue(persist_file=queue_file)
        stats2 = queue2.get_stats()
        assert stats2['total'] == stats['total'], "Persistence failed"
        print(f"  Persistence verified: {stats2}")
        
        print("\n✅ All tests passed!")
        return True
        
    finally:
        # Cleanup
        Path(queue_file).unlink(missing_ok=True)


def test_queue_change_callback():
    """Test that callbacks are triggered on queue changes."""
    print("\nTesting queue change callbacks...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        queue_file = f.name
    
    try:
        callback_count = [0]  # Use list to avoid scope issues
        
        def on_change():
            callback_count[0] += 1
        
        queue = DownloadQueue(on_change=on_change, persist_file=queue_file)
        
        # Add items should trigger callback
        queue.add("https://example.com/test", "/downloads")
        assert callback_count[0] > 0, "Callback should be triggered on add"
        
        print(f"✓ Callback triggered {callback_count[0]} time(s)")
        print("✅ Callback test passed!")
        return True
        
    finally:
        Path(queue_file).unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        test_queue_basic_workflow()
        test_queue_change_callback()
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
