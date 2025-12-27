"""
Unit tests for Download Job Queue System.

Tests the models, history database, and queue manager.
"""
import json
import os
import pytest
import tempfile
import threading
import time
from unittest.mock import Mock, patch

from downloader.models import (
    JobStatus, ItemStatus, DownloadEventType,
    DownloadJob, DownloadEvent,
    job_added_event, job_started_event, job_progress_event,
    item_progress_event, item_done_event, job_done_event,
    job_error_event, log_event
)
from downloader.history import DownloadHistoryDB
from downloader.queue import DownloadQueueManager
from downloader.base import BaseDownloader, DownloadResult, DownloadOptions


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_history.db")
        db = DownloadHistoryDB(db_path)
        yield db


@pytest.fixture
def sample_job():
    """Create a sample job for testing."""
    return DownloadJob.create(
        url="https://example.com/video.mp4",
        engine="TestEngine",
        output_folder="/tmp/downloads",
        options={"download_images": True, "max_retries": 3}
    )


@pytest.fixture
def sample_event(sample_job):
    """Create a sample event for testing."""
    return job_added_event(sample_job)


class FakeDownloader(BaseDownloader):
    """Fake downloader for testing the queue."""
    
    def __init__(self, *args, result=None, delay=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self._result = result or DownloadResult(
            success=True,
            total_files=1,
            completed_files=1
        )
        self._delay = delay
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return True
    
    def supports_url(self, url: str) -> bool:
        return True
    
    def get_site_name(self) -> str:
        return "FakeDownloader"
    
    def download(self, url: str) -> DownloadResult:
        # Simulate download with delay
        time.sleep(self._delay)
        
        # Check cancellation
        if self.is_cancelled():
            return DownloadResult(
                success=False,
                total_files=1,
                completed_files=0,
                error_message="Cancelled"
            )
        
        # Report some progress
        self.total_files = self._result.total_files
        self.completed_files = self._result.completed_files
        self.report_global_progress()
        
        return self._result


# ============================================================================
# Model Tests
# ============================================================================

class TestJobStatus:
    """Test JobStatus enum."""
    
    def test_all_statuses_exist(self):
        """Verify all expected statuses exist."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.PAUSED.value == "paused"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"


class TestDownloadJob:
    """Test DownloadJob dataclass."""
    
    def test_create_job(self):
        """Test job creation with factory method."""
        job = DownloadJob.create(
            url="https://example.com/video.mp4",
            engine="TestEngine",
            output_folder="/downloads"
        )
        
        assert job.id is not None
        assert len(job.id) == 36  # UUID format
        assert job.url == "https://example.com/video.mp4"
        assert job.engine == "TestEngine"
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
    
    def test_job_to_dict(self, sample_job):
        """Test job serialization to dict."""
        data = sample_job.to_dict()
        
        assert data['id'] == sample_job.id
        assert data['url'] == sample_job.url
        assert data['status'] == 'pending'
        assert isinstance(data['options_snapshot'], dict)
    
    def test_job_from_dict(self, sample_job):
        """Test job deserialization from dict."""
        data = sample_job.to_dict()
        restored = DownloadJob.from_dict(data)
        
        assert restored.id == sample_job.id
        assert restored.url == sample_job.url
        assert restored.status == sample_job.status
    
    def test_job_json_roundtrip(self, sample_job):
        """Test job JSON serialization roundtrip."""
        json_str = sample_job.to_json()
        restored = DownloadJob.from_json(json_str)
        
        assert restored.id == sample_job.id
        assert restored.url == sample_job.url
    
    def test_mark_started(self, sample_job):
        """Test marking job as started."""
        sample_job.mark_started()
        
        assert sample_job.status == JobStatus.RUNNING
        assert sample_job.started_at is not None
    
    def test_mark_completed(self, sample_job):
        """Test marking job as completed."""
        sample_job.mark_completed()
        
        assert sample_job.status == JobStatus.COMPLETED
        assert sample_job.finished_at is not None
    
    def test_mark_failed(self, sample_job):
        """Test marking job as failed."""
        sample_job.mark_failed("Connection error")
        
        assert sample_job.status == JobStatus.FAILED
        assert sample_job.error_message == "Connection error"
        assert sample_job.finished_at is not None
    
    def test_update_progress(self, sample_job):
        """Test updating job progress."""
        sample_job.update_progress(
            total_items=10,
            completed_items=5,
            failed_items=1
        )
        
        assert sample_job.total_items == 10
        assert sample_job.completed_items == 5
        assert sample_job.failed_items == 1


class TestDownloadEvent:
    """Test DownloadEvent dataclass."""
    
    def test_create_event(self):
        """Test event creation with factory method."""
        event = DownloadEvent.create(
            DownloadEventType.JOB_ADDED,
            "test-job-id",
            url="https://example.com"
        )
        
        assert event.type == DownloadEventType.JOB_ADDED
        assert event.job_id == "test-job-id"
        assert event.timestamp is not None
        assert event.payload['url'] == "https://example.com"
    
    def test_event_to_dict(self, sample_event):
        """Test event serialization to dict."""
        data = sample_event.to_dict()
        
        assert data['type'] == 'job_added'
        assert data['job_id'] == sample_event.job_id
    
    def test_event_json_roundtrip(self, sample_event):
        """Test event JSON serialization roundtrip."""
        json_str = sample_event.to_json()
        restored = DownloadEvent.from_json(json_str)
        
        assert restored.type == sample_event.type
        assert restored.job_id == sample_event.job_id


class TestEventFactoryFunctions:
    """Test convenience functions for creating events."""
    
    def test_job_added_event(self, sample_job):
        """Test job_added_event function."""
        event = job_added_event(sample_job)
        
        assert event.type == DownloadEventType.JOB_ADDED
        assert event.job_id == sample_job.id
        assert event.payload['url'] == sample_job.url
    
    def test_job_progress_event(self, sample_job):
        """Test job_progress_event function."""
        event = job_progress_event(sample_job, 5, 10)
        
        assert event.type == DownloadEventType.JOB_PROGRESS
        assert event.payload['completed_items'] == 5
        assert event.payload['total_items'] == 10
    
    def test_item_progress_event(self):
        """Test item_progress_event function."""
        event = item_progress_event(
            job_id="test-job",
            downloaded_bytes=1024,
            total_bytes=2048,
            file_id="file-1",
            speed=100.0
        )
        
        assert event.type == DownloadEventType.ITEM_PROGRESS
        assert event.payload['downloaded_bytes'] == 1024
        assert event.payload['speed'] == 100.0
    
    def test_log_event(self):
        """Test log_event function."""
        event = log_event("test-job", "Download started", "info")
        
        assert event.type == DownloadEventType.LOG
        assert event.payload['message'] == "Download started"
        assert event.payload['level'] == "info"


# ============================================================================
# History Database Tests
# ============================================================================

class TestDownloadHistoryDB:
    """Test DownloadHistoryDB persistence."""
    
    def test_save_and_get_job(self, temp_db, sample_job):
        """Test saving and retrieving a job."""
        temp_db.save_job(sample_job)
        
        retrieved = temp_db.get_job(sample_job.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_job.id
        assert retrieved.url == sample_job.url
        assert retrieved.engine == sample_job.engine
    
    def test_update_job(self, temp_db, sample_job):
        """Test updating an existing job."""
        temp_db.save_job(sample_job)
        
        sample_job.mark_started()
        sample_job.update_progress(total_items=10)
        temp_db.save_job(sample_job)
        
        retrieved = temp_db.get_job(sample_job.id)
        
        assert retrieved.status == JobStatus.RUNNING
        assert retrieved.total_items == 10
    
    def test_list_jobs(self, temp_db):
        """Test listing jobs."""
        # Add multiple jobs
        for i in range(5):
            job = DownloadJob.create(
                url=f"https://example.com/video{i}.mp4",
                engine="TestEngine",
                output_folder="/downloads"
            )
            temp_db.save_job(job)
        
        jobs = temp_db.list_jobs()
        
        assert len(jobs) == 5
    
    def test_list_jobs_with_status_filter(self, temp_db):
        """Test listing jobs filtered by status."""
        # Add jobs with different statuses
        for i in range(3):
            job = DownloadJob.create(
                url=f"https://example.com/video{i}.mp4",
                engine="TestEngine",
                output_folder="/downloads"
            )
            if i == 0:
                job.mark_completed()
            temp_db.save_job(job)
        
        pending_jobs = temp_db.list_jobs(status=JobStatus.PENDING)
        completed_jobs = temp_db.list_jobs(status=JobStatus.COMPLETED)
        
        assert len(pending_jobs) == 2
        assert len(completed_jobs) == 1
    
    def test_append_and_get_events(self, temp_db, sample_job, sample_event):
        """Test appending and retrieving events."""
        temp_db.save_job(sample_job)
        temp_db.append_event(sample_event)
        
        # Add more events
        started_event = job_started_event(sample_job)
        temp_db.append_event(started_event)
        
        events = temp_db.get_job_events(sample_job.id)
        
        assert len(events) == 2
        assert events[0].type == DownloadEventType.JOB_ADDED
        assert events[1].type == DownloadEventType.JOB_STARTED
    
    def test_delete_job(self, temp_db, sample_job, sample_event):
        """Test deleting a job and its events."""
        temp_db.save_job(sample_job)
        temp_db.append_event(sample_event)
        
        deleted = temp_db.delete_job(sample_job.id)
        
        assert deleted is True
        assert temp_db.get_job(sample_job.id) is None
        assert len(temp_db.get_job_events(sample_job.id)) == 0
    
    def test_get_stats(self, temp_db):
        """Test getting database statistics."""
        # Add jobs with different statuses
        for status in [JobStatus.PENDING, JobStatus.COMPLETED, JobStatus.FAILED]:
            job = DownloadJob.create(
                url="https://example.com/video.mp4",
                engine="TestEngine",
                output_folder="/downloads"
            )
            job.status = status
            temp_db.save_job(job)
        
        stats = temp_db.get_stats()
        
        assert stats['total'] == 3
        assert stats.get('pending', 0) == 1
        assert stats.get('completed', 0) == 1
        assert stats.get('failed', 0) == 1
    
    def test_thread_safety(self, temp_db):
        """Test that database operations are thread-safe."""
        results = []
        
        def save_jobs():
            for i in range(10):
                job = DownloadJob.create(
                    url=f"https://example.com/thread{threading.current_thread().name}/{i}.mp4",
                    engine="TestEngine",
                    output_folder="/downloads"
                )
                temp_db.save_job(job)
                results.append(job.id)
        
        threads = [threading.Thread(target=save_jobs) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All jobs should be saved
        jobs = temp_db.list_jobs(limit=100)
        assert len(jobs) == 30


# ============================================================================
# Queue Manager Tests
# ============================================================================

class TestDownloadQueueManager:
    """Test DownloadQueueManager."""
    
    @pytest.fixture
    def queue_manager(self, temp_db):
        """Create a queue manager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DownloadQueueManager(
                download_folder=tmpdir,
                history_db=temp_db,
                max_workers=1
            )
            yield manager
            if manager.is_running():
                manager.stop()
    
    def test_add_job_emits_event(self, queue_manager):
        """Test that adding a job emits JOB_ADDED event."""
        events = []
        queue_manager.event_callback = lambda e: events.append(e)
        
        with patch.object(
            DownloadQueueManager,
            '_process_job',
            return_value=None
        ):
            job_id = queue_manager.add_job("https://example.com/video.mp4")
        
        assert len(events) == 1
        assert events[0].type == DownloadEventType.JOB_ADDED
        assert events[0].job_id == job_id
    
    def test_job_lifecycle_events(self, queue_manager):
        """Test full job lifecycle emits correct events."""
        events = []
        queue_manager.event_callback = lambda e: events.append(e)
        
        # Mock the downloader factory to return our fake downloader
        with patch(
            'downloader.queue.DownloaderFactory.get_downloader'
        ) as mock_factory:
            mock_factory.return_value = FakeDownloader(
                download_folder=queue_manager.download_folder,
                delay=0.05
            )
            
            job_id = queue_manager.add_job("https://example.com/video.mp4")
            queue_manager.start()
            
            # Wait for job to complete
            time.sleep(0.5)
            queue_manager.stop()
        
        # Check event sequence
        event_types = [e.type for e in events]
        
        assert DownloadEventType.JOB_ADDED in event_types
        assert DownloadEventType.JOB_STARTED in event_types
        assert DownloadEventType.JOB_DONE in event_types or \
               DownloadEventType.JOB_PROGRESS in event_types
    
    def test_get_job(self, queue_manager):
        """Test retrieving a job by ID."""
        with patch.object(
            DownloadQueueManager,
            '_process_job',
            return_value=None
        ):
            job_id = queue_manager.add_job("https://example.com/video.mp4")
        
        job = queue_manager.get_job(job_id)
        
        assert job is not None
        assert job.id == job_id
        assert job.url == "https://example.com/video.mp4"
    
    def test_list_jobs(self, queue_manager):
        """Test listing all jobs."""
        with patch.object(
            DownloadQueueManager,
            '_process_job',
            return_value=None
        ):
            queue_manager.add_job("https://example.com/video1.mp4")
            queue_manager.add_job("https://example.com/video2.mp4")
        
        jobs = queue_manager.list_jobs()
        
        assert len(jobs) == 2
    
    def test_cancel_pending_job(self, queue_manager):
        """Test cancelling a pending job."""
        events = []
        queue_manager.event_callback = lambda e: events.append(e)
        
        with patch.object(
            DownloadQueueManager,
            '_process_job',
            return_value=None
        ):
            job_id = queue_manager.add_job("https://example.com/video.mp4")
        
        result = queue_manager.cancel_job(job_id)
        
        assert result is True
        
        job = queue_manager.get_job(job_id)
        assert job.status == JobStatus.CANCELLED
    
    def test_history_persistence(self, queue_manager, temp_db):
        """Test that jobs are persisted to history database."""
        with patch.object(
            DownloadQueueManager,
            '_process_job',
            return_value=None
        ):
            job_id = queue_manager.add_job("https://example.com/video.mp4")
        
        # Job should be in database
        db_job = temp_db.get_job(job_id)
        
        assert db_job is not None
        assert db_job.url == "https://example.com/video.mp4"
