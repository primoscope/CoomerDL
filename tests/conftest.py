"""
Pytest configuration and shared fixtures.
"""
import pytest
from downloader.base import DownloadOptions


@pytest.fixture
def download_folder(tmp_path):
    """
    Provide a temporary download folder for tests.
    
    Args:
        tmp_path: pytest's built-in tmp_path fixture
        
    Returns:
        Path object for temporary download folder
    """
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    return str(download_dir)


@pytest.fixture
def download_options():
    """
    Provide default download options for tests.
    
    Returns:
        DownloadOptions with standard default settings
    """
    return DownloadOptions(
        download_images=True,
        download_videos=True,
        download_compressed=True,
        download_documents=True,
        max_retries=3,
        retry_interval=2.0,
        chunk_size=1048576,
        timeout=30,
        min_file_size=0,
        max_file_size=0,
    )
