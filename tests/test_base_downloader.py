"""
Unit tests for BaseDownloader class.
"""
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult


class MockDownloader(BaseDownloader):
    """Mock downloader for testing BaseDownloader functionality."""
    
    def supports_url(self, url: str) -> bool:
        """Mock implementation - supports all URLs."""
        return True
    
    def get_site_name(self) -> str:
        """Mock implementation - returns test site name."""
        return "MockSite"
    
    def download(self, url: str) -> DownloadResult:
        """Mock implementation - returns successful result."""
        return DownloadResult(
            success=True,
            total_files=0,
            completed_files=0,
        )


class TestBaseDownloaderInitialization:
    """Test BaseDownloader initialization."""
    
    def test_init_with_folder(self, download_folder):
        """Test initialization with download folder."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.download_folder == download_folder
        assert downloader.options is not None
        assert isinstance(downloader.options, DownloadOptions)
    
    def test_init_with_options(self, download_folder, download_options):
        """Test initialization with custom options."""
        downloader = MockDownloader(
            download_folder=download_folder,
            options=download_options
        )
        assert downloader.options == download_options
        assert downloader.options.download_images is True
        assert downloader.options.max_retries == 3
    
    def test_init_with_callbacks(self, download_folder):
        """Test initialization with callbacks."""
        log_messages = []
        progress_updates = []
        
        def log_callback(msg):
            log_messages.append(msg)
        
        def progress_callback(downloaded, total, metadata):
            progress_updates.append((downloaded, total))
        
        downloader = MockDownloader(
            download_folder=download_folder,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )
        
        # Test log callback
        downloader.log("Test message")
        assert len(log_messages) == 1
        assert log_messages[0] == "Test message"
        
        # Test progress callback
        downloader.report_progress(50, 100)
        assert len(progress_updates) == 1
        assert progress_updates[0] == (50, 100)
    
    def test_init_default_translation(self, download_folder):
        """Test that default translation function works."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.tr("test") == "test"


class TestBaseDownloaderCancellation:
    """Test BaseDownloader cancellation mechanism."""
    
    def test_initial_state_not_cancelled(self, download_folder):
        """Test that downloader starts in non-cancelled state."""
        downloader = MockDownloader(download_folder=download_folder)
        assert not downloader.is_cancelled()
        assert not downloader.cancel_event.is_set()
    
    def test_request_cancel(self, download_folder):
        """Test requesting cancellation."""
        downloader = MockDownloader(download_folder=download_folder)
        downloader.request_cancel()
        assert downloader.is_cancelled()
        assert downloader.cancel_event.is_set()
    
    def test_request_cancel_with_log(self, download_folder):
        """Test that cancel logs a message."""
        log_messages = []
        
        def log_callback(msg):
            log_messages.append(msg)
        
        downloader = MockDownloader(
            download_folder=download_folder,
            log_callback=log_callback
        )
        downloader.request_cancel()
        
        assert downloader.is_cancelled()
        assert len(log_messages) == 1
        assert "cancel" in log_messages[0].lower()
    
    def test_reset_clears_cancel(self, download_folder):
        """Test that reset clears cancellation state."""
        downloader = MockDownloader(download_folder=download_folder)
        downloader.request_cancel()
        assert downloader.is_cancelled()
        
        downloader.reset()
        assert not downloader.is_cancelled()
        assert not downloader.cancel_event.is_set()
    
    def test_reset_clears_progress(self, download_folder):
        """Test that reset clears progress tracking."""
        downloader = MockDownloader(download_folder=download_folder)
        downloader.total_files = 10
        downloader.completed_files = 5
        downloader.failed_files = ["file1.jpg"]
        downloader.skipped_files = ["file2.mp4"]
        
        downloader.reset()
        
        assert downloader.total_files == 0
        assert downloader.completed_files == 0
        assert downloader.failed_files == []
        assert downloader.skipped_files == []


class TestBaseDownloaderFilenameSanitization:
    """Test BaseDownloader filename sanitization."""
    
    def test_sanitize_simple_filename(self):
        """Test sanitizing a simple valid filename."""
        result = BaseDownloader.sanitize_filename("file.mp4")
        assert result == "file.mp4"
    
    def test_sanitize_filename_with_spaces(self):
        """Test sanitizing filename with spaces."""
        result = BaseDownloader.sanitize_filename("my file name.jpg")
        assert result == "my file name.jpg"
    
    def test_sanitize_filename_with_invalid_chars(self):
        """Test sanitizing filename with invalid characters."""
        result = BaseDownloader.sanitize_filename("File: Name?.mp4")
        assert result == "File_ Name_.mp4"
        assert ":" not in result
        assert "?" not in result
    
    def test_sanitize_filename_with_slashes(self):
        """Test sanitizing filename with path separators."""
        result = BaseDownloader.sanitize_filename("folder/file\\name.jpg")
        assert result == "folder_file_name.jpg"
        assert "/" not in result
        assert "\\" not in result
    
    def test_sanitize_filename_with_quotes(self):
        """Test sanitizing filename with quotes."""
        result = BaseDownloader.sanitize_filename('file"name.mp4')
        assert result == "file_name.mp4"
        assert '"' not in result
    
    def test_sanitize_filename_with_multiple_invalid(self):
        """Test sanitizing filename with multiple invalid characters."""
        result = BaseDownloader.sanitize_filename('<>:"/\\|?*test.mp4')
        assert result == "_________test.mp4"
    
    def test_sanitize_filename_preserves_extension(self):
        """Test that sanitization preserves file extension."""
        result = BaseDownloader.sanitize_filename("file:name?.mp4")
        assert result.endswith(".mp4")


class TestBaseDownloaderFileType:
    """Test BaseDownloader file type detection."""
    
    def test_get_file_type_image(self, download_folder):
        """Test detecting image file types."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.get_file_type("photo.jpg") == "image"
        assert downloader.get_file_type("image.png") == "image"
        assert downloader.get_file_type("pic.gif") == "image"
        assert downloader.get_file_type("IMG.JPEG") == "image"
    
    def test_get_file_type_video(self, download_folder):
        """Test detecting video file types."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.get_file_type("video.mp4") == "video"
        assert downloader.get_file_type("movie.mkv") == "video"
        assert downloader.get_file_type("clip.webm") == "video"
        assert downloader.get_file_type("MOVIE.AVI") == "video"
    
    def test_get_file_type_document(self, download_folder):
        """Test detecting document file types."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.get_file_type("doc.pdf") == "document"
        assert downloader.get_file_type("sheet.xlsx") == "document"
        assert downloader.get_file_type("presentation.pptx") == "document"
    
    def test_get_file_type_compressed(self, download_folder):
        """Test detecting compressed file types."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.get_file_type("archive.zip") == "compressed"
        assert downloader.get_file_type("backup.rar") == "compressed"
        assert downloader.get_file_type("data.7z") == "compressed"
    
    def test_get_file_type_other(self, download_folder):
        """Test detecting unknown file types."""
        downloader = MockDownloader(download_folder=download_folder)
        assert downloader.get_file_type("file.xyz") == "other"
        assert downloader.get_file_type("noextension") == "other"


class TestBaseDownloaderProgressReporting:
    """Test BaseDownloader progress reporting."""
    
    def test_report_progress_callback(self, download_folder):
        """Test that progress is reported via callback."""
        progress_calls = []
        
        def progress_callback(downloaded, total, metadata):
            progress_calls.append({
                'downloaded': downloaded,
                'total': total,
                'metadata': metadata
            })
        
        downloader = MockDownloader(
            download_folder=download_folder,
            progress_callback=progress_callback
        )
        
        downloader.report_progress(100, 200, filename="test.jpg")
        
        assert len(progress_calls) == 1
        assert progress_calls[0]['downloaded'] == 100
        assert progress_calls[0]['total'] == 200
        assert progress_calls[0]['metadata']['filename'] == "test.jpg"
    
    def test_report_global_progress(self, download_folder):
        """Test global progress reporting."""
        global_progress_calls = []
        
        def global_progress_callback(completed, total):
            global_progress_calls.append((completed, total))
        
        downloader = MockDownloader(
            download_folder=download_folder,
            global_progress_callback=global_progress_callback
        )
        
        downloader.total_files = 10
        downloader.completed_files = 3
        downloader.report_global_progress()
        
        assert len(global_progress_calls) == 1
        assert global_progress_calls[0] == (3, 10)
    
    def test_enable_widgets_callback(self, download_folder):
        """Test enable/disable widgets callback."""
        widget_states = []
        
        def enable_widgets_callback(enabled):
            widget_states.append(enabled)
        
        downloader = MockDownloader(
            download_folder=download_folder,
            enable_widgets_callback=enable_widgets_callback
        )
        
        downloader.enable_widgets(False)
        downloader.enable_widgets(True)
        
        assert len(widget_states) == 2
        assert widget_states[0] is False
        assert widget_states[1] is True
