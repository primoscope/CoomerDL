"""
Tests for downloader utility functions.
Tests filename sanitization and generation without modifying the source code.
"""
import pytest
from downloader.downloader import Downloader


class TestSanitizeFilename:
    """Test the sanitize_filename method that removes invalid characters."""
    
    def setup_method(self):
        """Set up a minimal Downloader instance for testing."""
        self.downloader = Downloader(
            download_folder="/tmp/test",
            max_workers=1,
            log_callback=None
        )
    
    def test_sanitize_basic_filename(self):
        """Test that valid filenames pass through unchanged."""
        result = self.downloader.sanitize_filename("simple_filename.jpg")
        assert result == "simple_filename.jpg"
    
    def test_sanitize_removes_invalid_chars(self):
        """Test that invalid characters are replaced with underscores."""
        result = self.downloader.sanitize_filename('file<name>with:invalid"chars.jpg')
        assert result == "file_name_with_invalid_chars.jpg"
    
    def test_sanitize_removes_pipe_and_question(self):
        """Test removal of pipe and question mark characters."""
        result = self.downloader.sanitize_filename("file|name?test.png")
        assert result == "file_name_test.png"
    
    def test_sanitize_removes_asterisk(self):
        """Test removal of asterisk character."""
        result = self.downloader.sanitize_filename("file*name.mp4")
        assert result == "file_name.mp4"
    
    def test_sanitize_windows_path_separators(self):
        """Test removal of Windows path separators."""
        result = self.downloader.sanitize_filename("folder\\subfolder/file.txt")
        assert result == "folder_subfolder_file.txt"


class TestGetFilename:
    """Test the get_filename method that generates filenames in different modes."""
    
    def setup_method(self):
        """Set up a minimal Downloader instance for testing."""
        self.downloader = Downloader(
            download_folder="/tmp/test",
            max_workers=1,
            log_callback=None
        )
    
    def test_mode_0_original_name(self):
        """Test mode 0: original filename with attachment index."""
        self.downloader.file_naming_mode = 0
        result = self.downloader.get_filename(
            media_url="https://example.com/image.jpg",
            attachment_index=1
        )
        assert result == "image_1.jpg"
    
    def test_mode_0_with_query_params(self):
        """Test mode 0 strips query parameters from URL."""
        self.downloader.file_naming_mode = 0
        result = self.downloader.get_filename(
            media_url="https://example.com/photo.png?size=large",
            attachment_index=2
        )
        assert result == "photo_2.png"
    
    def test_mode_1_post_name_with_hash(self):
        """Test mode 1: post name with attachment index and hash."""
        self.downloader.file_naming_mode = 1
        result = self.downloader.get_filename(
            media_url="https://example.com/file.jpg",
            post_name="My Post Title",
            attachment_index=3
        )
        # Should contain sanitized post name, index, and hash
        assert "My Post Title" in result
        assert "_3_" in result
        assert result.endswith(".jpg")
    
    def test_mode_1_fallback_without_post_name(self):
        """Test mode 1 fallback when no post name provided."""
        self.downloader.file_naming_mode = 1
        result = self.downloader.get_filename(
            media_url="https://example.com/file.mp4",
            post_id="12345",
            attachment_index=1
        )
        assert "post_12345" in result
        assert "_1_" in result
        assert result.endswith(".mp4")
    
    def test_mode_2_post_name_with_post_id(self):
        """Test mode 2: post name with post ID and attachment index."""
        self.downloader.file_naming_mode = 2
        result = self.downloader.get_filename(
            media_url="https://example.com/video.webm",
            post_id="99999",
            post_name="Test Post",
            attachment_index=2
        )
        assert result == "Test Post - 99999_2.webm"
    
    def test_mode_2_without_post_id(self):
        """Test mode 2 without post ID."""
        self.downloader.file_naming_mode = 2
        result = self.downloader.get_filename(
            media_url="https://example.com/image.gif",
            post_name="No ID Post",
            attachment_index=1
        )
        assert result == "No ID Post_1.gif"
    
    def test_mode_3_with_timestamp(self):
        """Test mode 3: timestamp, post name, index, and hash."""
        self.downloader.file_naming_mode = 3
        result = self.downloader.get_filename(
            media_url="https://example.com/file.png",
            post_name="Timestamped Post",
            post_time="2024-01-15",
            attachment_index=1
        )
        assert "2024-01-15" in result
        assert "Timestamped Post" in result
        assert "_1_" in result
        assert result.endswith(".png")
    
    def test_mode_3_fallback_no_time(self):
        """Test mode 3 without timestamp provided."""
        self.downloader.file_naming_mode = 3
        result = self.downloader.get_filename(
            media_url="https://example.com/file.jpg",
            post_name="No Time",
            attachment_index=1
        )
        # Should still work but with empty time
        assert "No Time" in result
        assert result.endswith(".jpg")
    
    def test_default_mode_fallback(self):
        """Test that invalid mode falls back to basic sanitization."""
        self.downloader.file_naming_mode = 999
        result = self.downloader.get_filename(
            media_url="https://example.com/fallback.mp4",
            attachment_index=1
        )
        assert result == "fallback.mp4"
    
    def test_sanitizes_special_chars_in_post_name(self):
        """Test that special characters in post names are sanitized."""
        self.downloader.file_naming_mode = 2
        result = self.downloader.get_filename(
            media_url="https://example.com/file.jpg",
            post_id="123",
            post_name='Post<with>invalid:chars"test',
            attachment_index=1
        )
        assert "Post_with_invalid_chars_test" in result
