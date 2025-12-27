"""
Unit tests for Gallery Downloader, Policies, and Rate Limiter.
"""
import pytest
import threading
import time
from unittest.mock import patch

from downloader.policies import (
    RetryPolicy, DomainPolicy, compute_backoff, compute_backoff_sequence,
    DEFAULT_RETRY_POLICY
)
from downloader.ratelimiter import DomainLimiter, extract_domain
from downloader.gallery import GalleryDownloader, GalleryOptions
from downloader.factory import DownloaderFactory
from downloader.base import BaseDownloader, DownloadResult


# ============================================================================
# Policy Tests
# ============================================================================

class TestRetryPolicy:
    """Test RetryPolicy dataclass."""
    
    def test_default_values(self):
        """Test default policy values."""
        policy = RetryPolicy()
        
        assert policy.max_attempts == 5
        assert policy.base_delay == 1.0
        assert policy.max_delay == 30.0
        assert policy.jitter == 0.2
        assert 429 in policy.retryable_statuses
        assert 500 in policy.retryable_statuses
    
    def test_is_retryable_status(self):
        """Test status code checking."""
        policy = RetryPolicy()
        
        assert policy.is_retryable_status(429) is True
        assert policy.is_retryable_status(500) is True
        assert policy.is_retryable_status(200) is False
        assert policy.is_retryable_status(404) is False
    
    def test_is_retryable_exception(self):
        """Test exception checking."""
        from requests.exceptions import ConnectionError, Timeout
        
        policy = RetryPolicy()
        
        assert policy.is_retryable_exception(ConnectionError()) is True
        assert policy.is_retryable_exception(Timeout()) is True
        assert policy.is_retryable_exception(ValueError()) is False


class TestComputeBackoff:
    """Test backoff computation."""
    
    def test_exponential_growth(self):
        """Test that backoff grows exponentially."""
        policy = RetryPolicy(base_delay=1.0, max_delay=100.0, jitter=0)
        
        delays = [compute_backoff(i, policy) for i in range(5)]
        
        # Should be: 1, 2, 4, 8, 16
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0
        assert delays[4] == 16.0
    
    def test_max_delay_cap(self):
        """Test that backoff is capped at max_delay."""
        policy = RetryPolicy(base_delay=1.0, max_delay=5.0, jitter=0)
        
        delay = compute_backoff(10, policy)  # Would be 1024 without cap
        
        assert delay == 5.0
    
    def test_jitter_adds_variation(self):
        """Test that jitter adds randomness."""
        policy = RetryPolicy(base_delay=10.0, jitter=0.2)
        
        # Generate multiple values
        delays = [compute_backoff(0, policy) for _ in range(100)]
        
        # Should have variation (not all the same)
        assert len(set(delays)) > 1
        
        # All should be within jitter range (10 +/- 20%)
        for delay in delays:
            assert 8.0 <= delay <= 12.0
    
    def test_deterministic_without_jitter(self):
        """Test that jitter=0 produces deterministic results."""
        policy = RetryPolicy(base_delay=1.0, jitter=0)
        
        delays1 = [compute_backoff(i, policy) for i in range(3)]
        delays2 = [compute_backoff(i, policy) for i in range(3)]
        
        assert delays1 == delays2
    
    def test_backoff_sequence(self):
        """Test computing full backoff sequence."""
        policy = RetryPolicy(max_attempts=4, base_delay=1.0, max_delay=10.0)
        
        sequence = compute_backoff_sequence(policy)
        
        # Should have max_attempts - 1 delays
        assert len(sequence) == 3


class TestDomainPolicy:
    """Test DomainPolicy dataclass."""
    
    def test_default_values(self):
        """Test default policy values."""
        policy = DomainPolicy()
        
        assert policy.per_domain_max_concurrency == 2
        assert policy.min_interval_seconds == 1.0


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestExtractDomain:
    """Test domain extraction."""
    
    def test_basic_extraction(self):
        """Test basic domain extraction."""
        assert extract_domain("https://example.com/path") == "example.com"
        assert extract_domain("http://sub.example.com") == "sub.example.com"
    
    def test_removes_www(self):
        """Test that www prefix is removed."""
        assert extract_domain("https://www.example.com") == "example.com"
    
    def test_removes_port(self):
        """Test that port is removed."""
        assert extract_domain("https://example.com:8080/path") == "example.com"
    
    def test_handles_invalid_urls(self):
        """Test handling of invalid URLs."""
        assert extract_domain("not-a-url") == "unknown"
        assert extract_domain("") == "unknown"


class TestDomainLimiter:
    """Test DomainLimiter class."""
    
    def test_basic_acquire_release(self):
        """Test basic acquire/release cycle."""
        policy = DomainPolicy(per_domain_max_concurrency=2, min_interval_seconds=0)
        limiter = DomainLimiter(policy)
        
        limiter.acquire("example.com")
        limiter.release("example.com")
        
        # Should not raise
        assert True
    
    def test_context_manager(self):
        """Test context manager interface."""
        policy = DomainPolicy(per_domain_max_concurrency=2, min_interval_seconds=0)
        limiter = DomainLimiter(policy)
        
        with limiter.limit("example.com"):
            pass
        
        # Should not raise
        assert True
    
    def test_concurrency_limit(self):
        """Test that concurrency limit is enforced."""
        policy = DomainPolicy(per_domain_max_concurrency=2, min_interval_seconds=0)
        limiter = DomainLimiter(policy)
        
        active_count = [0]
        max_seen = [0]
        
        def worker():
            with limiter.limit("example.com"):
                active_count[0] += 1
                max_seen[0] = max(max_seen[0], active_count[0])
                time.sleep(0.1)
                active_count[0] -= 1
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Max concurrent should not exceed limit
        assert max_seen[0] <= 2
    
    def test_interval_enforcement(self):
        """Test that minimum interval is enforced."""
        policy = DomainPolicy(per_domain_max_concurrency=1, min_interval_seconds=0.2)
        limiter = DomainLimiter(policy)
        
        start = time.time()
        
        with limiter.limit("example.com"):
            pass
        
        with limiter.limit("example.com"):
            pass
        
        elapsed = time.time() - start
        
        # Should have waited at least min_interval between requests
        assert elapsed >= 0.2


# ============================================================================
# Gallery Downloader Tests
# ============================================================================

class TestGalleryDownloaderCanHandle:
    """Test GalleryDownloader URL handling."""
    
    def test_rejects_native_domains(self):
        """Test that native downloader domains are rejected."""
        assert GalleryDownloader.can_handle("https://coomer.su/profile") is False
        assert GalleryDownloader.can_handle("https://kemono.su/user") is False
        assert GalleryDownloader.can_handle("https://bunkr.site/album") is False
    
    def test_accepts_known_gallery_domains(self):
        """Test that known gallery domains are accepted."""
        # These may require gallery-dl to be installed for extractor check
        # but the domain check should work without it
        assert GalleryDownloader.can_handle("https://imgur.com/gallery/abc") is True
        assert GalleryDownloader.can_handle("https://deviantart.com/user") is True
    
    def test_rejects_invalid_urls(self):
        """Test that invalid URLs are rejected."""
        assert GalleryDownloader.can_handle("not-a-url") is False
        assert GalleryDownloader.can_handle("ftp://example.com") is False


class TestGalleryOptions:
    """Test GalleryOptions dataclass."""
    
    def test_default_values(self):
        """Test default option values."""
        opts = GalleryOptions()
        
        assert opts.enabled is True
        assert opts.write_metadata_json is True
        assert opts.write_urls is False
        assert opts.max_items is None
    
    def test_custom_values(self):
        """Test custom option values."""
        opts = GalleryOptions(
            enabled=False,
            max_items=100,
            sleep_interval=2.0
        )
        
        assert opts.enabled is False
        assert opts.max_items == 100
        assert opts.sleep_interval == 2.0


# ============================================================================
# Factory Routing Tests
# ============================================================================

class FakeGalleryDownloader(BaseDownloader):
    """Fake gallery downloader for testing."""
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return 'fake-gallery' in url.lower()
    
    def supports_url(self, url: str) -> bool:
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        return "FakeGallery"
    
    def download(self, url: str) -> DownloadResult:
        return DownloadResult(success=True, total_files=1, completed_files=1)


class TestFactoryRoutingPrecedence:
    """Test factory routing precedence."""
    
    @pytest.fixture(autouse=True)
    def clear_registry(self):
        """Clear factory registry before each test."""
        DownloaderFactory.clear_registry()
        yield
        DownloaderFactory.clear_registry()
    
    def test_native_downloader_takes_precedence(self):
        """Test that native downloaders are tried first."""
        DownloaderFactory.register(FakeGalleryDownloader)
        
        downloader = DownloaderFactory.get_downloader(
            url="https://fake-gallery.com/album",
            download_folder="/tmp",
            use_gallery_fallback=True,
            use_ytdlp_fallback=True
        )
        
        assert downloader is not None
        assert isinstance(downloader, FakeGalleryDownloader)
    
    def test_gallery_fallback_used_when_enabled(self):
        """Test that gallery fallback is used for gallery URLs."""
        # Mock GalleryDownloader.can_handle to return True
        with patch('downloader.gallery.GalleryDownloader.can_handle', return_value=True):
            with patch('downloader.gallery.GalleryDownloader') as MockGallery:
                MockGallery.can_handle.return_value = True
                
                downloader = DownloaderFactory.get_downloader(
                    url="https://imgur.com/gallery/test",
                    download_folder="/tmp",
                    use_gallery_fallback=True,
                    use_ytdlp_fallback=False,
                    use_generic_fallback=False
                )
                
                # Gallery should have been checked
                MockGallery.can_handle.assert_called_once()


# ============================================================================
# History Job Items Tests
# ============================================================================

class TestHistoryJobItems:
    """Test job items functionality in history."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database."""
        import tempfile
        import os
        from downloader.history import DownloadHistoryDB
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = DownloadHistoryDB(db_path)
            yield db
    
    def test_mark_job_item_done(self, temp_db):
        """Test marking job items as done."""
        from downloader.models import DownloadJob
        
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        temp_db.save_job(job)
        
        temp_db.mark_job_item_done(
            job.id,
            "https://example.com/image1.jpg",
            "/tmp/image1.jpg",
            "completed"
        )
        
        items = temp_db.get_job_items(job.id)
        
        assert len(items) == 1
        assert items[0]['item_key'] == "https://example.com/image1.jpg"
        assert items[0]['status'] == "completed"
    
    def test_get_completed_item_keys(self, temp_db):
        """Test getting completed item keys."""
        from downloader.models import DownloadJob
        
        job = DownloadJob.create(
            url="https://example.com",
            engine="Test",
            output_folder="/tmp"
        )
        temp_db.save_job(job)
        
        # Add some items
        temp_db.mark_job_item_done(job.id, "item1", "/tmp/1.jpg", "completed")
        temp_db.mark_job_item_done(job.id, "item2", "/tmp/2.jpg", "skipped")
        temp_db.mark_job_item_done(job.id, "item3", "/tmp/3.jpg", "failed")
        
        completed = temp_db.get_completed_item_keys(job.id)
        
        # Only completed and skipped should be returned
        assert "item1" in completed
        assert "item2" in completed
        assert "item3" not in completed
    
    def test_get_resumable_jobs(self, temp_db):
        """Test getting resumable jobs."""
        from downloader.models import DownloadJob, JobStatus
        
        # Create jobs with different statuses
        pending_job = DownloadJob.create("url1", "Test", "/tmp")
        pending_job.status = JobStatus.PENDING
        temp_db.save_job(pending_job)
        
        running_job = DownloadJob.create("url2", "Test", "/tmp")
        running_job.status = JobStatus.RUNNING
        temp_db.save_job(running_job)
        
        completed_job = DownloadJob.create("url3", "Test", "/tmp")
        completed_job.status = JobStatus.COMPLETED
        temp_db.save_job(completed_job)
        
        resumable = temp_db.get_resumable_jobs()
        
        # Only pending and running should be returned
        assert len(resumable) == 2
        statuses = {j.status for j in resumable}
        assert JobStatus.PENDING in statuses
        assert JobStatus.RUNNING in statuses


# ============================================================================
# BaseDownloader Enhancement Tests
# ============================================================================

class TestBaseDownloaderEnhancements:
    """Test BaseDownloader enhancements."""
    
    def test_canonicalize_url_removes_fragment(self):
        """Test that URL canonicalization removes fragments."""
        url = "https://example.com/page#section"
        result = BaseDownloader.canonicalize_url(url)
        
        assert "#section" not in result
    
    def test_canonicalize_url_sorts_params(self):
        """Test that URL params are sorted."""
        url1 = "https://example.com?b=2&a=1"
        url2 = "https://example.com?a=1&b=2"
        
        result1 = BaseDownloader.canonicalize_url(url1)
        result2 = BaseDownloader.canonicalize_url(url2)
        
        assert result1 == result2
