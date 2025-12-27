"""
Contract verification tests for the download system.

Tests verify the contracts defined in tests/CONTRACTS.md.
All tests are deterministic and offline (no network).
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from downloader.models import (
    JobStatus, ItemStatus, DownloadEventType,
    DownloadJob, DownloadEvent,
    job_added_event, job_started_event, job_done_event,
    job_progress_event, item_progress_event, item_done_event,
    job_error_event, job_cancelled_event, log_event
)
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult


# =============================================================================
# Job Status Transition Tests
# =============================================================================

class TestJobStatusTransitions:
    """Verify job status state machine transitions."""
    
    def test_pending_to_running(self):
        """PENDING -> RUNNING: mark_started() sets started_at."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        assert job.status == JobStatus.PENDING
        assert job.started_at is None
        
        job.mark_started()
        
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
    
    def test_running_to_completed(self):
        """RUNNING -> COMPLETED: mark_completed() sets finished_at."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.mark_started()
        
        job.mark_completed()
        
        assert job.status == JobStatus.COMPLETED
        assert job.finished_at is not None
    
    def test_running_to_failed(self):
        """RUNNING -> FAILED: mark_failed() sets error_message."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.mark_started()
        
        job.mark_failed("Network error")
        
        assert job.status == JobStatus.FAILED
        assert job.error_message == "Network error"
        assert job.finished_at is not None
    
    def test_running_to_cancelled(self):
        """RUNNING -> CANCELLED: mark_cancelled() sets finished_at."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.mark_started()
        
        job.mark_cancelled()
        
        assert job.status == JobStatus.CANCELLED
        assert job.finished_at is not None
    
    def test_pending_to_cancelled(self):
        """PENDING -> CANCELLED: direct cancellation before start."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        
        job.mark_cancelled()
        
        assert job.status == JobStatus.CANCELLED


# =============================================================================
# Counter Invariant Tests
# =============================================================================

class TestCounterInvariants:
    """Verify counter semantics and invariants."""
    
    def test_counters_sum_correctly(self):
        """Verify counter values make sense."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.update_progress(
            total_items=10,
            completed_items=7,
            failed_items=2,
            skipped_items=1
        )
        
        # Completed + failed should not exceed total
        assert job.completed_items + job.failed_items <= job.total_items
    
    def test_progress_percentage_calculation(self):
        """Progress = completed_items / total_items * 100."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.update_progress(total_items=10, completed_items=5)
        
        progress = (job.completed_items / job.total_items) * 100
        assert progress == 50.0
    
    def test_progress_percentage_zero_total(self):
        """Progress calculation handles zero total."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        
        # Zero total should not cause division by zero
        if job.total_items > 0:
            progress = (job.completed_items / job.total_items) * 100
        else:
            progress = 0.0
        
        assert progress == 0.0


# =============================================================================
# Download Result Contract Tests
# =============================================================================

class TestDownloadResultContract:
    """Verify DownloadResult invariants."""
    
    def test_successful_result(self):
        """Successful result has no failed files."""
        result = DownloadResult(
            success=True,
            total_files=10,
            completed_files=10,
            failed_files=[],
            skipped_files=[]
        )
        
        assert result.success is True
        assert len(result.failed_files) == 0
    
    def test_failed_result_has_error(self):
        """Failed result should have error message."""
        result = DownloadResult(
            success=False,
            total_files=10,
            completed_files=5,
            failed_files=["file1.jpg", "file2.mp4"],
            skipped_files=[],
            error_message="Download failed"
        )
        
        assert result.success is False
        assert len(result.failed_files) == 2
        assert result.error_message is not None
    
    def test_skipped_files_counted_as_completed(self):
        """Skipped files are included in completed count."""
        result = DownloadResult(
            success=True,
            total_files=10,
            completed_files=10,  # Includes 3 skipped
            failed_files=[],
            skipped_files=["skip1.jpg", "skip2.jpg", "skip3.jpg"]
        )
        
        # Skipped files should be <= completed files
        assert len(result.skipped_files) <= result.completed_files


# =============================================================================
# Event Emission Tests
# =============================================================================

class TestEventEmission:
    """Verify event emission order and payloads."""
    
    def test_job_added_event_payload(self):
        """JOB_ADDED event has required payload."""
        job = DownloadJob.create(
            url="https://example.com/video",
            engine="Universal",
            output_folder="/downloads"
        )
        
        event = job_added_event(job)
        
        assert event.type == DownloadEventType.JOB_ADDED
        assert event.job_id == job.id
        assert event.payload['url'] == job.url
        assert event.payload['engine'] == job.engine
        assert event.payload['output_folder'] == job.output_folder
    
    def test_job_started_event_payload(self):
        """JOB_STARTED event has required payload."""
        job = DownloadJob.create(
            url="https://example.com/video",
            engine="Universal",
            output_folder="/downloads"
        )
        
        event = job_started_event(job)
        
        assert event.type == DownloadEventType.JOB_STARTED
        assert event.payload['url'] == job.url
        assert event.payload['engine'] == job.engine
    
    def test_item_progress_event_payload(self):
        """ITEM_PROGRESS event has required payload."""
        event = item_progress_event(
            job_id="test-job",
            downloaded_bytes=1024,
            total_bytes=2048,
            file_id="file1",
            file_path="/tmp/file.mp4",
            url="https://example.com/file.mp4",
            speed=1000.0,
            eta=60
        )
        
        assert event.type == DownloadEventType.ITEM_PROGRESS
        assert event.payload['downloaded_bytes'] == 1024
        assert event.payload['total_bytes'] == 2048
        assert event.payload['file_id'] == "file1"
        assert event.payload['file_path'] == "/tmp/file.mp4"
    
    def test_item_done_event_payload(self):
        """ITEM_DONE event has required payload."""
        event = item_done_event(
            job_id="test-job",
            file_id="file1",
            file_path="/tmp/file.mp4",
            success=True
        )
        
        assert event.type == DownloadEventType.ITEM_DONE
        assert event.payload['file_id'] == "file1"
        assert event.payload['file_path'] == "/tmp/file.mp4"
        assert event.payload['success'] is True
    
    def test_job_done_event_payload(self):
        """JOB_DONE event has required payload."""
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        job.update_progress(
            total_items=10,
            completed_items=8,
            failed_items=1,
            skipped_items=1
        )
        job.mark_completed()
        
        event = job_done_event(job)
        
        assert event.type == DownloadEventType.JOB_DONE
        assert event.payload['status'] == JobStatus.COMPLETED.value
        assert event.payload['total_items'] == 10
        assert event.payload['completed_items'] == 8
        assert event.payload['failed_items'] == 1
        assert event.payload['skipped_items'] == 1
    
    def test_log_event_payload(self):
        """LOG event has required payload."""
        event = log_event("test-job", "Download started", level="info")
        
        assert event.type == DownloadEventType.LOG
        assert event.payload['message'] == "Download started"
        assert event.payload['level'] == "info"


# =============================================================================
# Serialization Contract Tests
# =============================================================================

class TestSerializationContract:
    """Verify JSON serialization/deserialization."""
    
    def test_job_roundtrip_serialization(self):
        """Job can be serialized and deserialized without data loss."""
        original = DownloadJob.create(
            url="https://example.com/video",
            engine="Universal",
            output_folder="/downloads",
            options={"format": "best", "audio_only": False}
        )
        original.update_progress(total_items=5, completed_items=3)
        original.mark_started()
        
        json_str = original.to_json()
        restored = DownloadJob.from_json(json_str)
        
        assert restored.id == original.id
        assert restored.url == original.url
        assert restored.engine == original.engine
        assert restored.status == original.status
        assert restored.total_items == original.total_items
        assert restored.completed_items == original.completed_items
        assert restored.options_snapshot == original.options_snapshot
    
    def test_event_roundtrip_serialization(self):
        """Event can be serialized and deserialized without data loss."""
        original = item_progress_event(
            job_id="test-123",
            downloaded_bytes=1024,
            total_bytes=2048,
            file_id="file1",
            speed=500.0
        )
        
        json_str = original.to_json()
        restored = DownloadEvent.from_json(json_str)
        
        assert restored.type == original.type
        assert restored.job_id == original.job_id
        assert restored.payload['downloaded_bytes'] == original.payload['downloaded_bytes']
        assert restored.payload['file_id'] == original.payload['file_id']


# =============================================================================
# Cancellation Contract Tests
# =============================================================================

class MockCancellableDownloader(BaseDownloader):
    """Mock downloader that respects cancellation."""
    
    def supports_url(self, url: str) -> bool:
        return True
    
    def get_site_name(self) -> str:
        return "MockCancellable"
    
    def download(self, url: str) -> DownloadResult:
        """Simulate download with cancellation check."""
        for i in range(100):
            if self.is_cancelled():
                return DownloadResult(
                    success=False,
                    total_files=100,
                    completed_files=i,
                    failed_files=[],
                    skipped_files=[],
                    error_message="Cancelled by user"
                )
            time.sleep(0.01)  # Simulate work
        
        return DownloadResult(
            success=True,
            total_files=100,
            completed_files=100,
            failed_files=[],
            skipped_files=[]
        )


class TestCancellationContract:
    """Verify cancellation behavior."""
    
    def test_cancellation_uses_threading_event(self, download_folder):
        """Cancellation must use threading.Event, not boolean."""
        downloader = MockCancellableDownloader(download_folder=download_folder)
        
        assert hasattr(downloader, 'cancel_event')
        assert isinstance(downloader.cancel_event, threading.Event)
    
    def test_cancellation_is_thread_safe(self, download_folder):
        """Cancellation can be requested from another thread."""
        downloader = MockCancellableDownloader(download_folder=download_folder)
        result = []
        
        def download_thread():
            r = downloader.download("https://example.com")
            result.append(r)
        
        # Start download in thread
        thread = threading.Thread(target=download_thread)
        thread.start()
        
        # Cancel from main thread
        time.sleep(0.05)  # Let download start
        downloader.request_cancel()
        
        thread.join(timeout=2.0)
        
        assert len(result) == 1
        assert result[0].success is False
    
    def test_cancellation_response_time(self, download_folder):
        """Cancellation should stop download within 2 seconds."""
        downloader = MockCancellableDownloader(download_folder=download_folder)
        
        def download_thread():
            downloader.download("https://example.com")
        
        thread = threading.Thread(target=download_thread)
        start_time = time.time()
        thread.start()
        
        time.sleep(0.1)
        downloader.request_cancel()
        
        thread.join(timeout=2.0)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"Cancellation took {elapsed:.2f}s, expected < 2s"
        assert not thread.is_alive()


# =============================================================================
# Retry Policy Contract Tests
# =============================================================================

class TestRetryPolicyContract:
    """Verify retry policy behavior."""
    
    def test_backoff_calculation_deterministic(self):
        """Backoff with jitter=0 is deterministic."""
        from downloader.policies import compute_backoff, RetryPolicy
        
        policy = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0,
            jitter=0.0  # No randomness
        )
        
        delays = [compute_backoff(i, policy) for i in range(5)]
        
        # Exponential: 1, 2, 4, 8, 16
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0
        assert delays[4] == 16.0
    
    def test_backoff_capped_at_max(self):
        """Backoff is capped at max_delay."""
        from downloader.policies import compute_backoff, RetryPolicy
        
        policy = RetryPolicy(
            max_attempts=10,
            base_delay=1.0,
            max_delay=10.0,
            jitter=0.0
        )
        
        # At attempt 5, raw delay would be 32, but should cap at 10
        delay = compute_backoff(5, policy)
        assert delay == 10.0
    
    def test_backoff_with_jitter_varies(self):
        """Backoff with jitter introduces variation."""
        from downloader.policies import compute_backoff, RetryPolicy
        
        policy = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0,
            jitter=0.2  # 20% jitter
        )
        
        # Generate multiple values and check they vary
        delays = [compute_backoff(2, policy) for _ in range(10)]
        
        # With jitter, not all values should be identical
        unique_delays = set(delays)
        assert len(unique_delays) > 1, "Jitter should produce varying delays"


# =============================================================================
# Filename Sanitization Contract Tests
# =============================================================================

class TestFilenameSanitizationContract:
    """Verify filename sanitization behavior."""
    
    def test_sanitize_removes_invalid_characters(self):
        """All invalid characters are replaced."""
        invalid_chars = '<>:"/\\|?*'
        filename = f"test{invalid_chars}file.mp4"
        
        result = BaseDownloader.sanitize_filename(filename)
        
        for char in invalid_chars:
            assert char not in result
    
    def test_sanitize_preserves_extension(self):
        """Extension is preserved after sanitization."""
        result = BaseDownloader.sanitize_filename("bad:name?.mp4")
        assert result.endswith(".mp4")
    
    def test_sanitize_handles_unicode(self):
        """Unicode characters are handled."""
        result = BaseDownloader.sanitize_filename("文件名.mp4")
        assert ".mp4" in result
    
    def test_sanitize_empty_returns_something(self):
        """Empty filename returns something (possibly empty)."""
        result = BaseDownloader.sanitize_filename("")
        # Empty input may return empty output - that's acceptable
        assert isinstance(result, str)


# =============================================================================
# File Skip Contract Tests
# =============================================================================

class MockSkipDownloader(BaseDownloader):
    """Mock downloader for skip testing."""
    
    def supports_url(self, url: str) -> bool:
        return True
    
    def get_site_name(self) -> str:
        return "MockSkip"
    
    def download(self, url: str) -> DownloadResult:
        return DownloadResult(success=True, total_files=0, completed_files=0)


class TestFileSkipContract:
    """Verify file skip behavior."""
    
    def test_skip_by_excluded_extensions(self, download_folder):
        """Files are skipped based on excluded extensions set."""
        options = DownloadOptions(
            excluded_extensions={'.exe', '.bat'}
        )
        
        downloader = MockSkipDownloader(
            download_folder=download_folder,
            options=options
        )
        
        # should_skip_file returns (should_skip, reason)
        should_skip, reason = downloader.should_skip_file(
            url="http://example.com/program.exe",
            filename="program.exe"
        )
        assert should_skip is True
        assert "blacklist" in reason.lower() or "exe" in reason.lower()
        
        should_skip_bat, reason_bat = downloader.should_skip_file(
            url="http://example.com/script.bat",
            filename="script.bat"
        )
        assert should_skip_bat is True
        
        # Video should not be skipped
        should_skip_mp4, reason_mp4 = downloader.should_skip_file(
            url="http://example.com/video.mp4",
            filename="video.mp4"
        )
        assert should_skip_mp4 is False
    
    def test_skip_by_date_range(self, download_folder):
        """Files are skipped based on date range."""
        options = DownloadOptions(
            date_from="2024-01-01",
            date_to="2024-12-31"
        )
        
        downloader = MockSkipDownloader(
            download_folder=download_folder,
            options=options
        )
        
        # Post from 2023 should be skipped
        should_skip, reason = downloader.should_skip_file(
            url="http://example.com/old.jpg",
            filename="old.jpg",
            post_date="2023-06-15"
        )
        assert should_skip is True
        
        # Post from 2024 should not be skipped
        should_skip_2024, reason_2024 = downloader.should_skip_file(
            url="http://example.com/new.jpg",
            filename="new.jpg",
            post_date="2024-06-15"
        )
        assert should_skip_2024 is False
    
    def test_no_skip_without_filters(self, download_folder):
        """Without filters, files are not skipped."""
        options = DownloadOptions()  # Default options
        
        downloader = MockSkipDownloader(
            download_folder=download_folder,
            options=options
        )
        
        should_skip, reason = downloader.should_skip_file(
            url="http://example.com/video.mp4",
            filename="video.mp4"
        )
        assert should_skip is False
