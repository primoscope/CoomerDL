"""
Unit tests for DownloaderFactory.
"""
import pytest
from downloader.base import BaseDownloader, DownloadResult
from downloader.factory import DownloaderFactory


class DummyDownloader(BaseDownloader):
    """Dummy downloader for testing factory."""
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Lightweight check - supports URLs containing 'dummy'."""
        return 'dummy' in url.lower()
    
    def supports_url(self, url: str) -> bool:
        """Supports URLs containing 'dummy'."""
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        """Returns test site name."""
        return "DummySite"
    
    def download(self, url: str) -> DownloadResult:
        """Mock download."""
        return DownloadResult(success=True, total_files=0, completed_files=0)


class AnotherDummyDownloader(BaseDownloader):
    """Another dummy downloader for testing."""
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Lightweight check - supports URLs containing 'another'."""
        return 'another' in url.lower()
    
    def supports_url(self, url: str) -> bool:
        """Supports URLs containing 'another'."""
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        """Returns test site name."""
        return "AnotherSite"
    
    def download(self, url: str) -> DownloadResult:
        """Mock download."""
        return DownloadResult(success=True, total_files=0, completed_files=0)


@pytest.fixture(autouse=True)
def clear_factory_registry():
    """Clear factory registry before and after each test."""
    DownloaderFactory.clear_registry()
    yield
    DownloaderFactory.clear_registry()


class TestDownloaderFactoryRegistration:
    """Test downloader registration in factory."""
    
    def test_register_single_downloader(self):
        """Test registering a single downloader."""
        DownloaderFactory.register(DummyDownloader)
        
        sites = DownloaderFactory.get_supported_sites()
        # Sites now includes yt-dlp universal support
        assert "DummySite" in sites
        # Check that DummySite is in the native downloaders (not yt-dlp)
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 1
    
    def test_register_multiple_downloaders(self):
        """Test registering multiple downloaders."""
        DownloaderFactory.register(DummyDownloader)
        DownloaderFactory.register(AnotherDummyDownloader)
        
        sites = DownloaderFactory.get_supported_sites()
        assert "DummySite" in sites
        assert "AnotherSite" in sites
        # Check native downloaders count
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 2
    
    def test_register_same_downloader_twice(self):
        """Test that registering same downloader twice doesn't duplicate."""
        DownloaderFactory.register(DummyDownloader)
        DownloaderFactory.register(DummyDownloader)
        
        sites = DownloaderFactory.get_supported_sites()
        # Check native downloaders count (should be 1, not duplicated)
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 1
    
    def test_register_as_decorator(self):
        """Test using register as a decorator."""
        @DownloaderFactory.register
        class DecoratedDownloader(BaseDownloader):
            def supports_url(self, url: str) -> bool:
                return 'decorated' in url
            
            def get_site_name(self) -> str:
                return "DecoratedSite"
            
            def download(self, url: str) -> DownloadResult:
                return DownloadResult(success=True, total_files=0, completed_files=0)
        
        sites = DownloaderFactory.get_supported_sites()
        assert "DecoratedSite" in sites
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        DownloaderFactory.register(DummyDownloader)
        native_sites_before = [s for s in DownloaderFactory.get_supported_sites() if "yt-dlp" not in s]
        assert len(native_sites_before) == 1
        
        DownloaderFactory.clear_registry()
        native_sites_after = [s for s in DownloaderFactory.get_supported_sites() if "yt-dlp" not in s]
        assert len(native_sites_after) == 0


class TestDownloaderFactorySelection:
    """Test downloader selection by URL."""
    
    def test_get_downloader_matching_url(self, download_folder):
        """Test getting downloader for matching URL."""
        DownloaderFactory.register(DummyDownloader)
        
        downloader = DownloaderFactory.get_downloader(
            url="https://dummy.com/test",
            download_folder=download_folder
        )
        
        assert downloader is not None
        assert isinstance(downloader, DummyDownloader)
        assert downloader.download_folder == download_folder
    
    def test_get_downloader_no_match(self, download_folder):
        """Test that no downloader is returned for unsupported URL when fallbacks disabled."""
        DownloaderFactory.register(DummyDownloader)
        
        downloader = DownloaderFactory.get_downloader(
            url="https://unsupported.com/test",
            download_folder=download_folder,
            use_generic_fallback=False,
            use_ytdlp_fallback=False
        )
        
        assert downloader is None
    
    def test_get_downloader_ytdlp_fallback(self, download_folder):
        """Test that yt-dlp downloader is used as fallback for supported URLs."""
        DownloaderFactory.register(DummyDownloader)
        
        # URL that doesn't match DummyDownloader but should be handled by yt-dlp
        downloader = DownloaderFactory.get_downloader(
            url="https://youtube.com/watch?v=test",
            download_folder=download_folder,
            use_ytdlp_fallback=True,
            use_generic_fallback=False
        )
        
        # Should get YtDlpDownloader since URL is http/https and not in native domains
        assert downloader is not None
        assert downloader.get_site_name() == "Universal (yt-dlp)"
    
    def test_get_downloader_first_match(self, download_folder):
        """Test that first matching downloader is returned."""
        # Register downloaders in specific order
        DownloaderFactory.register(DummyDownloader)
        DownloaderFactory.register(AnotherDummyDownloader)
        
        # Test URL that matches first downloader
        downloader = DownloaderFactory.get_downloader(
            url="https://dummy.com/test",
            download_folder=download_folder
        )
        
        assert isinstance(downloader, DummyDownloader)
        
        # Test URL that matches second downloader
        downloader2 = DownloaderFactory.get_downloader(
            url="https://another.com/test",
            download_folder=download_folder
        )
        
        assert isinstance(downloader2, AnotherDummyDownloader)
    
    def test_get_downloader_with_options(self, download_folder, download_options):
        """Test getting downloader with custom options."""
        DownloaderFactory.register(DummyDownloader)
        
        downloader = DownloaderFactory.get_downloader(
            url="https://dummy.com/test",
            download_folder=download_folder,
            options=download_options
        )
        
        assert downloader is not None
        assert downloader.options == download_options
    
    def test_get_downloader_with_callbacks(self, download_folder):
        """Test getting downloader with callbacks."""
        log_messages = []
        
        def log_callback(msg):
            log_messages.append(msg)
        
        DownloaderFactory.register(DummyDownloader)
        
        downloader = DownloaderFactory.get_downloader(
            url="https://dummy.com/test",
            download_folder=download_folder,
            log_callback=log_callback
        )
        
        assert downloader is not None
        downloader.log("Test")
        assert len(log_messages) == 1


class TestDownloaderFactorySupportedSites:
    """Test getting list of supported sites."""
    
    def test_get_supported_sites_empty(self):
        """Test getting supported sites with no registered downloaders."""
        sites = DownloaderFactory.get_supported_sites()
        assert isinstance(sites, list)
        # Only yt-dlp should be present when no native downloaders registered
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 0
    
    def test_get_supported_sites_single(self):
        """Test getting supported sites with one downloader."""
        DownloaderFactory.register(DummyDownloader)
        
        sites = DownloaderFactory.get_supported_sites()
        assert "DummySite" in sites
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 1
        assert native_sites[0] == "DummySite"
    
    def test_get_supported_sites_multiple(self):
        """Test getting supported sites with multiple downloaders."""
        DownloaderFactory.register(DummyDownloader)
        DownloaderFactory.register(AnotherDummyDownloader)
        
        sites = DownloaderFactory.get_supported_sites()
        assert "DummySite" in sites
        assert "AnotherSite" in sites
        native_sites = [s for s in sites if "yt-dlp" not in s]
        assert len(native_sites) == 2
    
    def test_get_supported_sites_includes_ytdlp(self):
        """Test that yt-dlp universal support is included."""
        sites = DownloaderFactory.get_supported_sites()
        ytdlp_sites = [s for s in sites if "yt-dlp" in s]
        assert len(ytdlp_sites) == 1
        assert "Universal" in ytdlp_sites[0]
