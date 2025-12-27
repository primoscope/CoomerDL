"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
from pathlib import Path


@pytest.fixture
def mock_settings():
    """
    Provides a standard configuration dictionary for testing.
    """
    return {
        'max_downloads': 3,
        'folder_structure': 'default',
        'language': 'en',
        'theme': 'System',
        'download_images': True,
        'download_videos': True,
        'download_compressed': True,
        'rate_limit_interval': 1.0,
        'max_retries': 999999,
        'retry_interval': 1.0,
        'stream_read_timeout': 10
    }


@pytest.fixture
def temp_download_dir(tmp_path):
    """
    Provides a temporary directory for download testing.
    Uses pytest's tmp_path fixture.
    """
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    return download_dir
