"""
Generic Downloader - Fallback for unsupported sites.

Attempts to extract media from any URL by parsing HTML for common media tags.
"""
from __future__ import annotations

import os
import re
from typing import Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.factory import DownloaderFactory


@DownloaderFactory.register
class GenericDownloader(BaseDownloader):
    """
    Generic downloader that attempts to extract media from any URL.
    Acts as a fallback when no specific downloader matches.
    """
    
    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        **kwargs
    ):
        super().__init__(
            download_folder=download_folder,
            options=options,
            **kwargs
        )
        
        # Media file extensions to look for
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        self.video_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
        self.media_extensions = self.image_extensions | self.video_extensions
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Generic downloader is a fallback - always returns False for routing.
        The factory explicitly uses GenericDownloader when no other matches.
        """
        return False
    
    def supports_url(self, url: str) -> bool:
        """
        Generic downloader supports any URL as a last resort.
        Should be registered last in the factory so specific downloaders are tried first.
        """
        # Always return False so this is used as fallback only
        # The factory will explicitly use this when no other downloader matches
        return False
    
    def get_site_name(self) -> str:
        """Return the site name."""
        return "Generic"
    
    def download(self, url: str) -> DownloadResult:
        """
        Download media from a generic URL.
        
        Strategy:
        1. Parse the HTML page
        2. Extract all <img> tags
        3. Extract all <video> tags
        4. Find all <a> tags pointing to media files
        5. Download everything found
        """
        start_time = time.time()
        self.reset()
        
        try:
            self.log(self.tr(f"Attempting generic download from: {url}"))
            
            # Fetch the page
            response = self.safe_request(url)
            if not response:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="Failed to fetch URL"
                )
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get page title for folder name
            title_tag = soup.find('title')
            page_title = title_tag.get_text().strip() if title_tag else 'generic_download'
            folder_name = self.sanitize_filename(page_title)[:50]  # Limit length
            download_folder = os.path.join(self.download_folder, folder_name)
            os.makedirs(download_folder, exist_ok=True)
            
            media_urls = set()  # Use set to avoid duplicates
            
            # Extract images from <img> tags
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(url, src)
                    if self._is_media_url(full_url):
                        media_urls.add(full_url)
            
            # Extract videos from <video> and <source> tags
            for video in soup.find_all('video'):
                src = video.get('src')
                if src:
                    full_url = urljoin(url, src)
                    media_urls.add(full_url)
                
                # Check <source> tags inside <video>
                for source in video.find_all('source'):
                    src = source.get('src')
                    if src:
                        full_url = urljoin(url, src)
                        media_urls.add(full_url)
            
            # Extract links to media files
            for link in soup.find_all('a', href=True):
                href = link['href']
                if self._is_media_url(href):
                    full_url = urljoin(url, href)
                    media_urls.add(full_url)
            
            self.total_files = len(media_urls)
            self.log(self.tr(f"Found {self.total_files} media files"))
            
            if self.total_files == 0:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="No media files found on the page"
                )
            
            # Download all found media
            for media_url in media_urls:
                if self.is_cancelled():
                    break
                
                try:
                    filename = os.path.basename(urlparse(media_url).path)
                    if not filename or '.' not in filename:
                        # Generate filename from URL
                        filename = f"media_{self.completed_files + 1}{self._get_extension(media_url)}"
                    
                    filepath = os.path.join(download_folder, filename)
                    
                    # Download the file
                    if self.download_file(media_url, filepath):
                        self.completed_files += 1
                        self.log(self.tr(f"Downloaded: {filename}"))
                    else:
                        self.failed_files.append(media_url)
                    
                    self.report_global_progress()
                    
                except Exception as e:
                    self.log(self.tr(f"Error downloading {media_url}: {e}"))
                    self.failed_files.append(media_url)
            
            success = self.completed_files > 0 and not self.is_cancelled()
            
            return DownloadResult(
                success=success,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                elapsed_seconds=time.time() - start_time
            )
            
        except Exception as e:
            self.log(self.tr(f"Generic download error: {e}"))
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )
    
    def _is_media_url(self, url: str) -> bool:
        """Check if URL points to a media file."""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            return any(path.endswith(ext) for ext in self.media_extensions)
        except:
            return False
    
    def _get_extension(self, url: str) -> str:
        """Extract file extension from URL."""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            for ext in self.media_extensions:
                if path.endswith(ext):
                    return ext
            return '.bin'
        except:
            return '.bin'
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem usage."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        return filename if filename else 'download'
