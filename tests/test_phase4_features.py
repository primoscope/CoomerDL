"""
Tests for Phase 4: Network Configuration & Advanced Filtering
"""
import pytest
import time
import os
from downloader.throttle import BandwidthThrottle
from downloader.base import DownloadOptions, MediaItem, BaseDownloader


class TestBandwidthThrottle:
    """Test bandwidth throttling functionality."""
    
    def test_unlimited_no_throttle(self):
        """Test that unlimited bandwidth (0) doesn't throttle."""
        throttle = BandwidthThrottle(0)
        assert throttle.is_unlimited()
        
        start = time.time()
        # Should return immediately
        throttle.throttle(1024 * 1024)  # 1MB
        elapsed = time.time() - start
        
        # Should be nearly instant (less than 10ms)
        assert elapsed < 0.01
    
    def test_throttle_limits_speed(self):
        """Test that throttle actually limits bandwidth."""
        # Set limit to 100KB/s
        throttle = BandwidthThrottle(100 * 1024)
        
        start = time.time()
        # Download 100KB - should take ~1 second
        throttle.throttle(100 * 1024)
        elapsed = time.time() - start
        
        # Should take roughly 1 second (allow 0.5-2.0 for variance)
        assert 0.5 < elapsed < 2.0
    
    def test_set_limit_resets_counters(self):
        """Test that changing limit resets counters."""
        throttle = BandwidthThrottle(100 * 1024)
        throttle.throttle(50 * 1024)
        
        # Change limit
        throttle.set_limit(200 * 1024)
        
        # Should start fresh
        start = time.time()
        throttle.throttle(100 * 1024)
        elapsed = time.time() - start
        
        # Should take roughly 0.5 seconds at 200KB/s
        assert 0.3 < elapsed < 1.5
    
    def test_get_limit_conversions(self):
        """Test limit conversions to KB/s and MB/s."""
        throttle = BandwidthThrottle(1024 * 1024)  # 1MB/s
        
        assert throttle.get_limit_kbps() == 1024.0
        assert throttle.get_limit_mbps() == 1.0


class TestDownloadOptions:
    """Test DownloadOptions with new fields."""
    
    def test_default_options(self):
        """Test default option values."""
        options = DownloadOptions()
        
        # New network options
        assert options.bandwidth_limit_kbps == 0
        assert options.connection_timeout == 30
        assert options.read_timeout == 60
        
        # Filtering options
        assert options.min_file_size == 0
        assert options.max_file_size == 0
        assert options.date_from is None
        assert options.date_to is None
        assert options.excluded_extensions == set()
    
    def test_custom_bandwidth_limit(self):
        """Test setting custom bandwidth limit."""
        options = DownloadOptions(bandwidth_limit_kbps=500)
        assert options.bandwidth_limit_kbps == 500
    
    def test_custom_timeouts(self):
        """Test setting custom timeouts."""
        options = DownloadOptions(
            connection_timeout=60,
            read_timeout=120
        )
        assert options.connection_timeout == 60
        assert options.read_timeout == 120
    
    def test_file_size_filters(self):
        """Test file size filter options."""
        options = DownloadOptions(
            min_file_size=1024 * 1024,  # 1MB
            max_file_size=10 * 1024 * 1024  # 10MB
        )
        assert options.min_file_size == 1024 * 1024
        assert options.max_file_size == 10 * 1024 * 1024
    
    def test_date_filters(self):
        """Test date filter options."""
        options = DownloadOptions(
            date_from='2024-01-01',
            date_to='2024-12-31'
        )
        assert options.date_from == '2024-01-01'
        assert options.date_to == '2024-12-31'
    
    def test_excluded_extensions(self):
        """Test excluded extensions option."""
        excluded = {'.webm', '.gif'}
        options = DownloadOptions(excluded_extensions=excluded)
        assert options.excluded_extensions == excluded


class TestMediaItemFiltering:
    """Test media item filtering with should_download_file."""
    
    class MockDownloader(BaseDownloader):
        """Mock downloader for testing."""
        def supports_url(self, url: str) -> bool:
            return True
        
        def get_site_name(self) -> str:
            return "Mock"
        
        def download(self, url: str):
            pass
    
    def test_file_type_filtering(self):
        """Test filtering by file type."""
        options = DownloadOptions(
            download_images=True,
            download_videos=False
        )
        downloader = self.MockDownloader('/tmp', options)
        
        # Image should pass
        img_item = MediaItem(
            url='http://example.com/image.jpg',
            filename='image.jpg',
            file_type='image'
        )
        assert downloader.should_download_file(img_item)
        
        # Video should be filtered
        vid_item = MediaItem(
            url='http://example.com/video.mp4',
            filename='video.mp4',
            file_type='video'
        )
        assert not downloader.should_download_file(vid_item)
    
    def test_file_size_min_filtering(self):
        """Test filtering by minimum file size."""
        options = DownloadOptions(
            min_file_size=1024 * 1024  # 1MB
        )
        downloader = self.MockDownloader('/tmp', options)
        
        # Small file should be filtered
        small_item = MediaItem(
            url='http://example.com/small.jpg',
            filename='small.jpg',
            file_type='image',
            size=500 * 1024  # 500KB
        )
        assert not downloader.should_download_file(small_item)
        
        # Large file should pass
        large_item = MediaItem(
            url='http://example.com/large.jpg',
            filename='large.jpg',
            file_type='image',
            size=2 * 1024 * 1024  # 2MB
        )
        assert downloader.should_download_file(large_item)
    
    def test_file_size_max_filtering(self):
        """Test filtering by maximum file size."""
        options = DownloadOptions(
            max_file_size=10 * 1024 * 1024  # 10MB
        )
        downloader = self.MockDownloader('/tmp', options)
        
        # Small file should pass
        small_item = MediaItem(
            url='http://example.com/small.jpg',
            filename='small.jpg',
            file_type='image',
            size=5 * 1024 * 1024  # 5MB
        )
        assert downloader.should_download_file(small_item)
        
        # Large file should be filtered
        large_item = MediaItem(
            url='http://example.com/large.jpg',
            filename='large.jpg',
            file_type='image',
            size=20 * 1024 * 1024  # 20MB
        )
        assert not downloader.should_download_file(large_item)


class TestFiltersSettings:
    """Test filters settings integration."""
    
    def test_build_excluded_extensions(self):
        """Test building excluded extensions from settings."""
        filter_settings = {
            'exclude_webm': True,
            'exclude_gif': True,
            'exclude_webp': False,
            'exclude_zip': True,
            'exclude_rar': False,
        }
        
        excluded = set()
        if filter_settings.get('exclude_webm', False):
            excluded.add('.webm')
        if filter_settings.get('exclude_gif', False):
            excluded.add('.gif')
        if filter_settings.get('exclude_webp', False):
            excluded.add('.webp')
        if filter_settings.get('exclude_zip', False):
            excluded.add('.zip')
        if filter_settings.get('exclude_rar', False):
            excluded.add('.rar')
        
        assert '.webm' in excluded
        assert '.gif' in excluded
        assert '.webp' not in excluded
        assert '.zip' in excluded
        assert '.rar' not in excluded


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
