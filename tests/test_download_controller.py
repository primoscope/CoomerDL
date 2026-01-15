"""
Example test demonstrating DownloadController testability.

This shows how the controller can be tested independently of the UI layer.
"""

import unittest
from unittest.mock import MagicMock, patch
from app.controllers.download_controller import DownloadController, extract_ck_parameters, extract_ck_query
from urllib.parse import urlparse


class TestDownloadController(unittest.TestCase):
    """Test suite for DownloadController."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock callbacks
        self.log_callback = MagicMock()
        self.update_progress_callback = MagicMock()
        self.update_global_progress_callback = MagicMock()
        self.enable_widgets_callback = MagicMock()
        self.export_logs_callback = MagicMock()
        
        # Mock checkbox getters
        self.get_download_images = MagicMock(return_value=True)
        self.get_download_videos = MagicMock(return_value=True)
        self.get_download_compressed = MagicMock(return_value=True)
        self.get_download_documents = MagicMock(return_value=True)
        
        # Mock translation
        self.tr = MagicMock(side_effect=lambda x, **kwargs: x)
        
        # Create controller
        self.controller = DownloadController(
            download_folder='/tmp/test',
            settings={},
            max_downloads=3,
            log_callback=self.log_callback,
            update_progress_callback=self.update_progress_callback,
            update_global_progress_callback=self.update_global_progress_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            export_logs_callback=self.export_logs_callback,
            get_download_images=self.get_download_images,
            get_download_videos=self.get_download_videos,
            get_download_compressed=self.get_download_compressed,
            get_download_documents=self.get_download_documents,
            tr=self.tr,
            progress_manager=None,
            root=None
        )
    
    def test_controller_initialization(self):
        """Test controller initializes correctly."""
        self.assertEqual(self.controller.download_folder, '/tmp/test')
        self.assertEqual(self.controller.max_downloads, 3)
        self.assertIsNone(self.controller.get_active_downloader())
    
    def test_extract_ck_parameters_with_post(self):
        """Test extracting Coomer/Kemono parameters with post."""
        url = urlparse('https://coomer.st/onlyfans/user/testuser/post/12345')
        service, user, post = extract_ck_parameters(url)
        
        self.assertEqual(service, 'onlyfans')
        self.assertEqual(user, 'testuser')
        self.assertEqual(post, '12345')
    
    def test_extract_ck_parameters_without_post(self):
        """Test extracting Coomer/Kemono parameters without post."""
        url = urlparse('https://kemono.cr/patreon/user/testuser')
        service, user, post = extract_ck_parameters(url)
        
        self.assertEqual(service, 'patreon')
        self.assertEqual(user, 'testuser')
        self.assertIsNone(post)
    
    def test_extract_ck_query_with_params(self):
        """Test extracting query parameters."""
        url = urlparse('https://coomer.st/onlyfans/user/test?q=search&o=50')
        query, offset = extract_ck_query(url)
        
        self.assertEqual(query, 'search')
        self.assertEqual(offset, 50)
    
    def test_extract_ck_query_without_params(self):
        """Test extracting query without parameters."""
        url = urlparse('https://coomer.st/onlyfans/user/test')
        query, offset = extract_ck_query(url)
        
        self.assertEqual(query, '0')
        self.assertEqual(offset, 0)
    
    def test_get_active_downloader_initially_none(self):
        """Test active downloader is None initially."""
        self.assertIsNone(self.controller.get_active_downloader())


class TestDownloadControllerIntegration(unittest.TestCase):
    """Integration tests showing controller behavior."""
    
    def test_controller_can_be_created_with_minimal_config(self):
        """Test controller can be created with minimal configuration."""
        controller = DownloadController(
            download_folder='/tmp',
            settings={},
            max_downloads=3,
            log_callback=lambda msg: None,
            update_progress_callback=lambda a,b,c: None,
            update_global_progress_callback=lambda a,b: None,
            enable_widgets_callback=lambda: None,
            export_logs_callback=lambda: None,
            get_download_images=lambda: True,
            get_download_videos=lambda: True,
            get_download_compressed=lambda: True,
            get_download_documents=lambda: True,
            tr=lambda x, **kwargs: x
        )
        
        self.assertIsNotNone(controller)
        self.assertEqual(controller.download_folder, '/tmp')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
