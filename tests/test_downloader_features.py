import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import time
from downloader.downloader import Downloader
from downloader.throttle import BandwidthThrottle

class TestDownloaderFeatures(unittest.TestCase):

    @patch('downloader.downloader.sqlite3.connect')
    @patch('downloader.downloader.os.makedirs')
    def setUp(self, mock_makedirs, mock_connect):
        self.mock_db = MagicMock()
        # Ensure fetchone returns None so is_url_downloaded returns False
        self.mock_db.cursor.return_value.fetchone.return_value = None
        mock_connect.return_value = self.mock_db

        # Initialize downloader with mocks and dummy tr
        self.downloader = Downloader(
            download_folder="test_downloads",
            max_workers=1,
            log_callback=MagicMock(),
            tr=lambda x, **kwargs: x.format(**kwargs) if kwargs else x
        )
        # Mock the session to prevent actual HTTP requests
        self.downloader.session = MagicMock()

    def test_file_size_filter_min(self):
        """Test that files below min_size are skipped."""
        self.downloader.min_size = 1024 * 1024  # 1 MB
        self.downloader.max_size = 0
        self.downloader.size_filter_enabled = True

        # Mock response with small file size
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '500'} # 500 bytes
        mock_response.status_code = 200
        self.downloader.safe_request = MagicMock(return_value=mock_response)

        # Call process_media_element
        self.downloader.process_media_element(
            media_url="http://example.com/small.jpg",
            user_id="user1",
            post_id="post1"
        )

        # Verify it didn't try to download content
        mock_response.iter_content.assert_not_called()
        self.downloader.log_callback.assert_any_call(ANY)

    def test_file_size_filter_max(self):
        """Test that files above max_size are skipped."""
        self.downloader.min_size = 0
        self.downloader.max_size = 1024 * 1024 # 1 MB
        self.downloader.size_filter_enabled = True

        # Mock response with large file size
        mock_response = MagicMock()
        mock_response.headers = {'content-length': str(2 * 1024 * 1024)} # 2 MB
        mock_response.status_code = 200
        self.downloader.safe_request = MagicMock(return_value=mock_response)

        self.downloader.process_media_element(
            media_url="http://example.com/large.jpg",
            user_id="user1",
            post_id="post1"
        )

        mock_response.iter_content.assert_not_called()

    @patch('downloader.downloader.as_completed')
    def test_date_range_filter(self, mock_as_completed):
        """Test that posts outside date range are skipped."""
        # Set date filters (YYYY-MM-DD)
        self.downloader.date_from = "2023-01-01"
        self.downloader.date_to = "2023-12-31"

        # Test posts with relative paths
        post_before = {'id': '1', 'published': '2022-12-31', 'file': {'path': '/1.jpg'}}
        post_in_range = {'id': '2', 'published': '2023-06-15', 'file': {'path': '/2.jpg'}}
        post_after = {'id': '3', 'published': '2024-01-01', 'file': {'path': '/3.jpg'}}

        # Mock fetch_user_posts
        self.downloader.fetch_user_posts = MagicMock(return_value=[post_before, post_in_range, post_after])
        self.downloader.process_media_element = MagicMock()
        self.downloader.executor = MagicMock()

        # Mock as_completed to return immediately
        mock_as_completed.return_value = []

        # Call download_media
        self.downloader.download_media(site="test.com", user_id="user1", service="service1")

        # Verify executor.submit calls
        # We expect 1 call for post_in_range ('https://test.com/2.jpg')
        self.assertEqual(self.downloader.executor.submit.call_count, 1)

        args, _ = self.downloader.executor.submit.call_args
        self.assertEqual(args[1], 'https://test.com/2.jpg')

    @patch('downloader.downloader.open')
    @patch('downloader.downloader.os.rename')
    @patch('downloader.downloader.os.path.exists')
    def test_bandwidth_throttling(self, mock_exists, mock_rename, mock_open):
        """Test that bandwidth throttling is applied."""
        self.downloader.bandwidth_limit_kbps = 100 # 100 KB/s
        self.downloader.throttle = MagicMock()

        mock_exists.return_value = False # File doesn't exist

        mock_response = MagicMock()
        mock_response.headers = {'content-length': '10240'}
        mock_response.status_code = 200
        # iter_content yields chunks
        mock_response.iter_content.return_value = [b'x' * 1024 for _ in range(10)]
        self.downloader.safe_request = MagicMock(return_value=mock_response)

        self.downloader.process_media_element(
            media_url="http://example.com/file.jpg",
            user_id="user1",
            post_id="post1"
        )

        # Verify throttle was called for each chunk
        self.assertTrue(self.downloader.throttle.throttle.called)
        self.assertEqual(self.downloader.throttle.throttle.call_count, 10)

if __name__ == '__main__':
    unittest.main()
