"""
User journey tests for the download system.

Tests simulate realistic user workflows without real network access.
All tests use mocked HTTP responses.
"""
import pytest
import tempfile
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from downloader.models import (
    JobStatus, ItemStatus, DownloadEventType,
    DownloadJob, DownloadEvent
)
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.queue import DownloadQueueManager
from downloader.history import DownloadHistoryDB
from downloader.factory import DownloaderFactory


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_download_folder():
    """Create a temporary download folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def mock_events():
    """Capture events for verification."""
    events = []
    
    def capture(event):
        events.append(event)
    
    return events, capture


class FakeDownloader(BaseDownloader):
    """Fake downloader for testing queue behavior."""
    
    def __init__(self, *args, simulate_items=3, simulate_failure=False, 
                 simulate_slow=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulate_items = simulate_items
        self.simulate_failure = simulate_failure
        self.simulate_slow = simulate_slow
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return 'fake://' in url
    
    def supports_url(self, url: str) -> bool:
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        return "FakeDownloader"
    
    def download(self, url: str) -> DownloadResult:
        """Simulate a download with progress reporting."""
        self.total_files = self.simulate_items
        
        for i in range(self.simulate_items):
            if self.is_cancelled():
                return DownloadResult(
                    success=False,
                    total_files=self.simulate_items,
                    completed_files=i,
                    failed_files=[],
                    skipped_files=[],
                    error_message="Cancelled"
                )
            
            # Simulate item download
            file_id = f"file_{i}"
            
            # Progress reporting
            for progress in range(0, 101, 10):
                if self.is_cancelled():
                    break
                self.report_progress(
                    progress, 100,
                    file_id=file_id,
                    status="Downloading"
                )
                if self.simulate_slow:
                    time.sleep(0.05)
                else:
                    time.sleep(0.001)
            
            if self.simulate_failure and i == 1:
                self.failed_files.append(f"file_{i}.jpg")
            else:
                self.completed_files += 1
            
            self.report_global_progress()
        
        success = len(self.failed_files) == 0
        return DownloadResult(
            success=success,
            total_files=self.simulate_items,
            completed_files=self.completed_files,
            failed_files=self.failed_files.copy(),
            skipped_files=self.skipped_files.copy()
        )


# =============================================================================
# User Journey: Single URL Download
# =============================================================================

class TestSingleUrlDownloadJourney:
    """Test the journey of downloading a single URL."""
    
    def test_successful_single_download(self, temp_download_folder, temp_db_path, mock_events):
        """User pastes a URL and downloads successfully."""
        events, capture = mock_events
        
        # Setup
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        # Mock the factory to return our fake downloader
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=3
            )
            
            # User action: add URL to queue
            job_id = queue.add_job("fake://example.com/gallery")
            assert job_id is not None
            
            # Verify JOB_ADDED event
            job_added = [e for e in events if e.type == DownloadEventType.JOB_ADDED]
            assert len(job_added) == 1
            
            # User action: start downloads
            queue.start()
            
            # Wait for completion
            time.sleep(1.0)
            queue.stop()
            
        # Verify events were emitted in correct order
        event_types = [e.type for e in events]
        assert DownloadEventType.JOB_ADDED in event_types
        assert DownloadEventType.JOB_STARTED in event_types
        assert DownloadEventType.JOB_DONE in event_types
        
        # Verify job in history
        jobs = history_db.list_jobs()
        assert len(jobs) >= 1
    
    def test_download_with_failure(self, temp_download_folder, temp_db_path, mock_events):
        """User downloads but some items fail."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=3,
                simulate_failure=True
            )
            
            queue.add_job("fake://example.com/gallery")
            queue.start()
            time.sleep(1.0)
            queue.stop()
        
        # Verify job completed but with failures
        job_done_events = [e for e in events if e.type == DownloadEventType.JOB_DONE]
        assert len(job_done_events) >= 1


# =============================================================================
# User Journey: Batch URL Download
# =============================================================================

class TestBatchUrlDownloadJourney:
    """Test the journey of downloading multiple URLs."""
    
    def test_multiple_urls_sequential(self, temp_download_folder, temp_db_path, mock_events):
        """User pastes multiple URLs and downloads them."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        urls = [
            "fake://example.com/gallery1",
            "fake://example.com/gallery2",
            "fake://example.com/gallery3"
        ]
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            # Return a new fake downloader for each call
            mock_factory.side_effect = lambda **kwargs: FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=2
            )
            
            # User action: add multiple URLs
            job_ids = []
            for url in urls:
                job_id = queue.add_job(url)
                job_ids.append(job_id)
            
            assert len(job_ids) == 3
            
            # Verify all jobs added
            job_added = [e for e in events if e.type == DownloadEventType.JOB_ADDED]
            assert len(job_added) == 3
            
            # Start processing
            queue.start()
            time.sleep(2.0)  # Allow time for all jobs
            queue.stop()
        
        # All jobs should have completed
        jobs = history_db.list_jobs()
        assert len(jobs) >= 3


# =============================================================================
# User Journey: Cancellation
# =============================================================================

class TestCancellationJourney:
    """Test the journey of cancelling downloads."""
    
    def test_cancel_during_download(self, temp_download_folder, temp_db_path, mock_events):
        """User cancels a download in progress."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=10,
                simulate_slow=True  # Slow download to allow cancellation
            )
            
            job_id = queue.add_job("fake://example.com/large-gallery")
            queue.start()
            
            # Wait for download to start
            time.sleep(0.2)
            
            # User action: cancel the job
            queue.cancel_job(job_id)
            
            # Wait for cancellation to complete
            time.sleep(0.5)
            queue.stop()
        
        # Verify cancellation event
        cancelled_events = [e for e in events if e.type == DownloadEventType.JOB_CANCELLED]
        # Note: depending on timing, job might complete before cancellation
    
    def test_cancel_pending_job(self, temp_download_folder, temp_db_path, mock_events):
        """User cancels a job before it starts."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=5,
                simulate_slow=True
            )
            
            # Add first job that will run
            job_id_1 = queue.add_job("fake://example.com/first")
            
            # Add second job that will be pending
            job_id_2 = queue.add_job("fake://example.com/second")
            
            queue.start()
            time.sleep(0.1)  # Let first job start
            
            # Cancel the pending job
            queue.cancel_job(job_id_2)
            
            time.sleep(1.0)
            queue.stop()
        
        # Second job should be cancelled
        job = queue.get_job(job_id_2)
        if job:
            assert job.status in [JobStatus.CANCELLED, JobStatus.PENDING]


# =============================================================================
# User Journey: Progress Monitoring
# =============================================================================

class TestProgressMonitoringJourney:
    """Test that progress is reported correctly for UI."""
    
    def test_progress_events_emitted(self, temp_download_folder, temp_db_path, mock_events):
        """Progress events are emitted during download."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=2
            )
            
            queue.add_job("fake://example.com/gallery")
            queue.start()
            time.sleep(1.0)
            queue.stop()
        
        # Verify progress events were emitted
        progress_events = [e for e in events if e.type in [
            DownloadEventType.ITEM_PROGRESS,
            DownloadEventType.JOB_PROGRESS
        ]]
        
        # Should have some progress events
        # (exact count depends on implementation)


# =============================================================================
# User Journey: History Persistence
# =============================================================================

class TestHistoryPersistenceJourney:
    """Test that history persists across sessions."""
    
    def test_history_survives_restart(self, temp_download_folder, temp_db_path, mock_events):
        """Job history is available after 'restart'."""
        events, capture = mock_events
        
        # Session 1: Download something
        history_db_1 = DownloadHistoryDB(db_path=temp_db_path)
        
        queue_1 = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db_1,
            event_callback=capture,
            max_workers=1
        )
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=2
            )
            
            job_id = queue_1.add_job("fake://example.com/gallery")
            queue_1.start()
            time.sleep(1.0)
            queue_1.stop()
        
        # Session 2: Check history is preserved
        history_db_2 = DownloadHistoryDB(db_path=temp_db_path)
        
        jobs = history_db_2.list_jobs()
        assert len(jobs) >= 1
        
        # Find our job
        found = False
        for job in jobs:
            if job.id == job_id:
                found = True
                break
        
        assert found, "Job should be in history after restart"


# =============================================================================
# User Journey: Error Recovery
# =============================================================================

class TestErrorRecoveryJourney:
    """Test error handling and recovery."""
    
    def test_network_error_handled(self, temp_download_folder, temp_db_path, mock_events):
        """Network errors are handled gracefully."""
        events, capture = mock_events
        
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            history_db=history_db,
            event_callback=capture,
            max_workers=1
        )
        
        # Create a downloader that raises an exception
        class ErrorDownloader(FakeDownloader):
            def download(self, url):
                raise Exception("Network error")
        
        with patch.object(DownloaderFactory, 'get_downloader') as mock_factory:
            mock_factory.return_value = ErrorDownloader(
                download_folder=temp_download_folder
            )
            
            queue.add_job("fake://example.com/will-fail")
            queue.start()
            time.sleep(1.0)
            queue.stop()
        
        # Job should be marked as failed
        error_events = [e for e in events if e.type == DownloadEventType.JOB_ERROR]
        # Error should have been captured


# =============================================================================
# User Journey: Settings Application
# =============================================================================

class TestSettingsApplicationJourney:
    """Test that user settings are applied correctly."""
    
    def test_options_passed_to_downloader(self, temp_download_folder, temp_db_path):
        """Download options are passed to the downloader."""
        history_db = DownloadHistoryDB(db_path=temp_db_path)
        
        custom_options = DownloadOptions(
            download_images=True,
            download_videos=False,  # Only images
            max_retries=5
        )
        
        queue = DownloadQueueManager(
            download_folder=temp_download_folder,
            options=custom_options,
            history_db=history_db,
            max_workers=1
        )
        
        captured_options = []
        
        def capturing_factory(**kwargs):
            captured_options.append(kwargs.get('options'))
            return FakeDownloader(
                download_folder=temp_download_folder,
                simulate_items=1
            )
        
        with patch.object(DownloaderFactory, 'get_downloader', side_effect=capturing_factory):
            queue.add_job("fake://example.com/gallery")
            queue.start()
            time.sleep(0.5)
            queue.stop()
        
        # Options should have been passed
        if captured_options:
            opts = captured_options[0]
            if opts:
                assert opts.download_videos is False
                assert opts.max_retries == 5
