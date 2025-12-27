"""
Reddit Downloader - Official support for Reddit posts.

Uses Reddit's public JSON API to extract media from posts.
"""
import os
import re
import json
import time
from typing import Optional
from urllib.parse import urlparse
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.factory import DownloaderFactory


@DownloaderFactory.register
class RedditDownloader(BaseDownloader):
    """
    Reddit downloader using the public JSON API.
    Supports image and video downloads from Reddit posts.
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
    
    def supports_url(self, url: str) -> bool:
        """Check if this downloader can handle Reddit URLs."""
        return 'reddit.com' in url.lower() or 'redd.it' in url.lower()
    
    def get_site_name(self) -> str:
        """Return the site name."""
        return "Reddit"
    
    def download(self, url: str) -> DownloadResult:
        """
        Download media from a Reddit post.
        
        Reddit JSON API: Append .json to any Reddit URL to get JSON data.
        """
        start_time = time.time()
        self.reset()
        
        try:
            # Normalize URL and add .json
            json_url = self._get_json_url(url)
            self.log(self.tr(f"Fetching Reddit post: {json_url}"))
            
            # Fetch JSON data
            response = self.safe_request(json_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if not response:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="Failed to fetch Reddit JSON"
                )
            
            # Parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message=f"Failed to parse Reddit JSON: {e}"
                )
            
            # Extract post data
            if not data or len(data) < 1:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="Invalid Reddit JSON structure"
                )
            
            post_data = data[0]['data']['children'][0]['data']
            
            # Create download folder from post title
            post_title = post_data.get('title', 'reddit_post')
            folder_name = self.sanitize_filename(post_title)[:50]
            download_folder = os.path.join(self.download_folder, folder_name)
            os.makedirs(download_folder, exist_ok=True)
            
            # Extract media URLs
            media_urls = self._extract_media_urls(post_data)
            
            self.total_files = len(media_urls)
            self.log(self.tr(f"Found {self.total_files} media items"))
            
            if self.total_files == 0:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="No media found in Reddit post"
                )
            
            # Download all media
            for idx, media_url in enumerate(media_urls):
                if self.is_cancelled():
                    break
                
                try:
                    # Determine filename
                    ext = self._get_extension_from_url(media_url)
                    filename = f"{folder_name}_{idx + 1}{ext}"
                    filepath = os.path.join(download_folder, filename)
                    
                    # Download
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
            self.log(self.tr(f"Reddit download error: {e}"))
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )
    
    def _get_json_url(self, url: str) -> str:
        """Convert Reddit URL to JSON API URL."""
        # Remove trailing slash
        url = url.rstrip('/')
        
        # If already has .json, return as is
        if url.endswith('.json'):
            return url
        
        # Add .json to the URL
        return f"{url}.json"
    
    def _extract_media_urls(self, post_data: dict) -> list:
        """Extract media URLs from Reddit post data."""
        media_urls = []
        
        # Check for direct image link (url_overridden_by_dest)
        if 'url_overridden_by_dest' in post_data:
            url = post_data['url_overridden_by_dest']
            if self._is_direct_media(url):
                media_urls.append(url)
        
        # Check for Reddit video
        if 'secure_media' in post_data and post_data['secure_media']:
            reddit_video = post_data['secure_media'].get('reddit_video', {})
            if 'fallback_url' in reddit_video:
                # Reddit videos have separate audio/video streams
                # For MVP, just download the video stream
                video_url = reddit_video['fallback_url']
                media_urls.append(video_url)
        
        # Check for gallery (multiple images)
        if 'gallery_data' in post_data:
            gallery_items = post_data['gallery_data'].get('items', [])
            media_metadata = post_data.get('media_metadata', {})
            
            for item in gallery_items:
                media_id = item.get('media_id')
                if media_id in media_metadata:
                    media_info = media_metadata[media_id]
                    # Get highest quality version
                    if 's' in media_info:
                        image_url = media_info['s'].get('u')
                        if image_url:
                            # Unescape HTML entities
                            image_url = image_url.replace('&amp;', '&')
                            media_urls.append(image_url)
        
        # Check for preview images as fallback
        if not media_urls and 'preview' in post_data:
            preview = post_data['preview']
            if 'images' in preview and len(preview['images']) > 0:
                source = preview['images'][0].get('source', {})
                if 'url' in source:
                    image_url = source['url'].replace('&amp;', '&')
                    media_urls.append(image_url)
        
        return media_urls
    
    def _is_direct_media(self, url: str) -> bool:
        """Check if URL is a direct media link."""
        media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mov'}
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in media_extensions)
    
    def _get_extension_from_url(self, url: str) -> str:
        """Extract file extension from URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Common extensions
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mov']:
            if ext in path:
                return ext
        
        # Default based on common patterns
        if 'video' in url or 'mp4' in url:
            return '.mp4'
        else:
            return '.jpg'
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem usage."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        return filename if filename else 'reddit_post'
