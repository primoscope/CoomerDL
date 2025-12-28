"""
Universal Scraper - Intelligent media detection for any webpage.

Uses multiple extraction strategies to find and download media from any URL.
"""
import os
import re
import json
import time
import logging
from typing import Optional, List, Dict, Any, Set
from urllib.parse import urlparse, urljoin, unquote
from dataclasses import dataclass, field
from enum import Enum

from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.factory import DownloaderFactory

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Types of media that can be extracted."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    ARCHIVE = "archive"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


@dataclass
class MediaItem:
    """Represents a discovered media item."""
    url: str
    media_type: MediaType
    filename: str
    estimated_size: Optional[int] = None
    quality: Optional[str] = None  # e.g., "1080p", "720p", "best"
    format: Optional[str] = None  # e.g., "mp4", "jpg"
    source_strategy: Optional[str] = None  # Which strategy found this


@dataclass
class MediaAnalysisResult:
    """Result of analyzing a URL for media."""
    url: str
    site_name: str
    videos: List[MediaItem] = field(default_factory=list)
    images: List[MediaItem] = field(default_factory=list)
    audio: List[MediaItem] = field(default_factory=list)
    archives: List[MediaItem] = field(default_factory=list)
    documents: List[MediaItem] = field(default_factory=list)
    total_estimated_size: int = 0
    requires_auth: bool = False
    error_message: Optional[str] = None
    
    @property
    def all_media(self) -> List[MediaItem]:
        """Get all media items combined."""
        return self.videos + self.images + self.audio + self.archives + self.documents
    
    @property
    def total_items(self) -> int:
        """Get total number of media items."""
        return len(self.all_media)


class UniversalScraper(BaseDownloader):
    """
    Intelligent scraper that dynamically detects media on ANY webpage.
    
    Uses multiple strategies in order of preference:
    1. yt-dlp extraction (1000+ sites)
    2. gallery-dl extraction (100+ gallery sites)
    3. Open Graph meta tags
    4. JSON-LD structured data
    5. HTML5 video/audio tags
    6. Image tag extraction
    7. Direct file link detection
    8. iframe extraction
    """
    
    STRATEGIES = [
        'yt_dlp_extraction',
        'gallery_dl_extraction',
        'og_meta_extraction',
        'json_ld_extraction',
        'html5_video_extraction',
        'html5_audio_extraction',
        'image_extraction',
        'selenium_extraction', # New dynamic strategy
        'link_extraction',
        'iframe_extraction',
    ]
    
    # File extensions by media type
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.opus'}
    ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.epub'}
    
    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        enabled_strategies: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            download_folder=download_folder,
            options=options,
            **kwargs
        )
        self.enabled_strategies = enabled_strategies or self.STRATEGIES
        self._seen_urls: Set[str] = set()
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Universal scraper can handle any HTTP(S) URL."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https')
        except Exception:
            return False
    
    def supports_url(self, url: str) -> bool:
        """Check if URL is supported (any HTTP URL)."""
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        """Return the site name."""
        return "Universal Scraper"
    
    def analyze_page(self, url: str) -> MediaAnalysisResult:
        """
        Analyze a URL and return all found media with metadata.
        
        Args:
            url: The URL to analyze.
        
        Returns:
            MediaAnalysisResult with all discovered media.
        """
        result = MediaAnalysisResult(
            url=url,
            site_name=self._get_site_name_from_url(url)
        )
        
        self.log(self.tr(f"Analyzing URL: {url}"))
        
        # Try each enabled strategy
        for strategy_name in self.enabled_strategies:
            if self.is_cancelled():
                break
            
            try:
                strategy_method = getattr(self, f"_strategy_{strategy_name}", None)
                if strategy_method:
                    self.log(self.tr(f"Trying strategy: {strategy_name}"))
                    items = strategy_method(url)
                    
                    if items:
                        self.log(self.tr(f"Found {len(items)} items via {strategy_name}"))
                        self._categorize_items(items, result, strategy_name)
            except Exception as e:
                logger.warning(f"Strategy {strategy_name} failed for {url}: {e}")
        
        # Calculate total estimated size
        result.total_estimated_size = sum(
            item.estimated_size for item in result.all_media 
            if item.estimated_size
        )
        
        return result
    
    def _categorize_items(self, items: List[str], result: MediaAnalysisResult, strategy: str):
        """Categorize URLs into media types."""
        for url in items:
            # Skip duplicates
            if url in self._seen_urls:
                continue
            self._seen_urls.add(url)
            
            media_type = self._detect_media_type(url)
            filename = self._extract_filename(url)
            
            item = MediaItem(
                url=url,
                media_type=media_type,
                filename=filename,
                source_strategy=strategy
            )
            
            # Add to appropriate list
            if media_type == MediaType.VIDEO:
                result.videos.append(item)
            elif media_type == MediaType.IMAGE:
                result.images.append(item)
            elif media_type == MediaType.AUDIO:
                result.audio.append(item)
            elif media_type == MediaType.ARCHIVE:
                result.archives.append(item)
            elif media_type == MediaType.DOCUMENT:
                result.documents.append(item)
    
    def _detect_media_type(self, url: str) -> MediaType:
        """Detect media type from URL."""
        url_lower = url.lower()
        
        for ext in self.VIDEO_EXTENSIONS:
            if ext in url_lower:
                return MediaType.VIDEO
        
        for ext in self.IMAGE_EXTENSIONS:
            if ext in url_lower:
                return MediaType.IMAGE
        
        for ext in self.AUDIO_EXTENSIONS:
            if ext in url_lower:
                return MediaType.AUDIO
        
        for ext in self.ARCHIVE_EXTENSIONS:
            if ext in url_lower:
                return MediaType.ARCHIVE
        
        for ext in self.DOCUMENT_EXTENSIONS:
            if ext in url_lower:
                return MediaType.DOCUMENT
        
        return MediaType.UNKNOWN
    
    def _extract_filename(self, url: str) -> str:
        """Extract filename from URL."""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = os.path.basename(path)
        
        if not filename:
            filename = f"media_{hash(url) % 10000}"
        
        return filename
    
    def _get_site_name_from_url(self, url: str) -> str:
        """Extract site name from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "Unknown"
    
    def _strategy_yt_dlp_extraction(self, url: str) -> List[str]:
        """Extract media using yt-dlp."""
        try:
            from downloader.ytdlp_adapter import YtDlpDownloader
            
            # Check if yt-dlp can handle this
            if not YtDlpDownloader.can_handle(url):
                return []
            
            ytdlp = YtDlpDownloader(
                download_folder=self.download_folder,
                options=self.options
            )
            
            info = ytdlp.analyze_info(url)
            if info:
                # For now, just return the URL itself
                # yt-dlp will handle the actual download
                return [url]
            
        except ImportError:
            logger.debug("yt-dlp not available")
        except Exception as e:
            logger.debug(f"yt-dlp extraction failed: {e}")
        
        return []
    
    def _strategy_gallery_dl_extraction(self, url: str) -> List[str]:
        """Extract media using gallery-dl."""
        try:
            from downloader.gallery import GalleryDownloader
            
            if not GalleryDownloader.can_handle(url):
                return []
            
            # Gallery-dl will handle this URL
            return [url]
            
        except ImportError:
            logger.debug("gallery-dl not available")
        except Exception as e:
            logger.debug(f"gallery-dl extraction failed: {e}")
        
        return []
    
    def _strategy_og_meta_extraction(self, url: str) -> List[str]:
        """Extract media from Open Graph meta tags."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for og:image, og:video, og:audio
            for tag in soup.find_all('meta', property=re.compile(r'^og:(image|video|audio)$')):
                content = tag.get('content')
                if content:
                    absolute_url = urljoin(url, content)
                    urls.append(absolute_url)
        
        except Exception as e:
            logger.debug(f"OG meta extraction failed: {e}")
        
        return urls
    
    def _strategy_json_ld_extraction(self, url: str) -> List[str]:
        """Extract media from JSON-LD structured data."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find JSON-LD scripts
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    urls.extend(self._extract_urls_from_json_ld(data))
                except json.JSONDecodeError:
                    continue
        
        except Exception as e:
            logger.debug(f"JSON-LD extraction failed: {e}")
        
        return urls
    
    def _extract_urls_from_json_ld(self, data: Any) -> List[str]:
        """Recursively extract URLs from JSON-LD data."""
        urls = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ('contentUrl', 'thumbnailUrl', 'url', 'image'):
                    if isinstance(value, str):
                        urls.append(value)
                    elif isinstance(value, list):
                        urls.extend([v for v in value if isinstance(v, str)])
                else:
                    urls.extend(self._extract_urls_from_json_ld(value))
        elif isinstance(data, list):
            for item in data:
                urls.extend(self._extract_urls_from_json_ld(item))
        
        return urls
    
    def _strategy_html5_video_extraction(self, url: str) -> List[str]:
        """Extract video from HTML5 <video> tags."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all video tags
            for video in soup.find_all('video'):
                # Check src attribute
                src = video.get('src')
                if src:
                    urls.append(urljoin(url, src))
                
                # Check source children
                for source in video.find_all('source'):
                    src = source.get('src')
                    if src:
                        urls.append(urljoin(url, src))
        
        except Exception as e:
            logger.debug(f"HTML5 video extraction failed: {e}")
        
        return urls
    
    def _strategy_html5_audio_extraction(self, url: str) -> List[str]:
        """Extract audio from HTML5 <audio> tags."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all audio tags
            for audio in soup.find_all('audio'):
                # Check src attribute
                src = audio.get('src')
                if src:
                    urls.append(urljoin(url, src))
                
                # Check source children
                for source in audio.find_all('source'):
                    src = source.get('src')
                    if src:
                        urls.append(urljoin(url, src))
        
        except Exception as e:
            logger.debug(f"HTML5 audio extraction failed: {e}")
        
        return urls
    
    def _strategy_image_extraction(self, url: str) -> List[str]:
        """Extract images from <img> tags with smart filtering."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all img tags
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    absolute_url = urljoin(url, src)
                    
                    # Filter out tiny images (icons, buttons, etc.)
                    width = img.get('width')
                    height = img.get('height')
                    
                    # Skip if dimensions are small
                    if width and height:
                        try:
                            if int(width) < 100 or int(height) < 100:
                                continue
                        except ValueError:
                            pass
                    
                    urls.append(absolute_url)
        
        except Exception as e:
            logger.debug(f"Image extraction failed: {e}")
        
        return urls
    
    def _strategy_link_extraction(self, url: str) -> List[str]:
        """Extract direct file links."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            all_extensions = (
                self.VIDEO_EXTENSIONS | self.IMAGE_EXTENSIONS | 
                self.AUDIO_EXTENSIONS | self.ARCHIVE_EXTENSIONS
            )
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                href_lower = href.lower()
                
                # Check if link points to a media file
                if any(ext in href_lower for ext in all_extensions):
                    absolute_url = urljoin(url, href)
                    urls.append(absolute_url)
        
        except Exception as e:
            logger.debug(f"Link extraction failed: {e}")
        
        return urls
    
    def _strategy_iframe_extraction(self, url: str) -> List[str]:
        """Extract embedded iframes (YouTube, Vimeo, etc.)."""
        urls = []
        
        try:
            response = self.safe_request(url)
            if not response:
                return []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all iframes
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    
                    # Only include if it looks like a video embed
                    if any(domain in absolute_url.lower() for domain in 
                           ['youtube.com', 'vimeo.com', 'dailymotion.com', 'twitch.tv']):
                        urls.append(absolute_url)
        
        except Exception as e:
            logger.debug(f"Iframe extraction failed: {e}")
        
        return urls
    
    def download(self, url: str) -> DownloadResult:
        """
        Download media from URL using intelligent detection.
        
        Args:
            url: The URL to download from.
        
        Returns:
            DownloadResult with statistics.
        """
        start_time = time.time()
        self.reset()
        self._seen_urls.clear()
        
        try:
            # Check for crawl mode
            if self.options.crawl_depth > 0:
                self.log(self.tr(f"Starting deep crawl with depth {self.options.crawl_depth}"))
                return self._download_recursive(url, depth=0)

            # Analyze the page first
            analysis = self.analyze_page(url)
            
            if analysis.error_message:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message=analysis.error_message,
                    elapsed_seconds=time.time() - start_time
                )
            
            self.total_files = analysis.total_items
            self.log(self.tr(f"Found {self.total_files} media items to download"))
            
            if self.total_files == 0:
                return DownloadResult(
                    success=False,
                    total_files=0,
                    completed_files=0,
                    error_message="No media found on page",
                    elapsed_seconds=time.time() - start_time
                )
            
            # Download all media
            for item in analysis.all_media:
                if self.is_cancelled():
                    break
                
                try:
                    # Create subfolder by media type
                    subfolder = os.path.join(self.download_folder, item.media_type.value)
                    os.makedirs(subfolder, exist_ok=True)
                    
                    filepath = os.path.join(subfolder, item.filename)
                    
                    # Download
                    if self.download_file(item.url, filepath):
                        self.completed_files += 1
                        self.log(self.tr(f"Downloaded: {item.filename}"))
                    else:
                        self.failed_files.append(item.url)
                    
                    self.report_global_progress()
                    
                except Exception as e:
                    self.log(self.tr(f"Error downloading {item.url}: {e}"))
                    self.failed_files.append(item.url)
            
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
            logger.error(f"Universal scraper error for {url}: {e}")
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )
    
    def download_all(
        self,
        url: str,
        media_types: Optional[List[str]] = None
    ) -> DownloadResult:
        """
        Download all media from URL with optional type filtering.
        
        Args:
            url: The URL to download from.
            media_types: Optional list of media types to download 
                        (e.g., ['video', 'image']).
        
        Returns:
            DownloadResult with statistics.
        """
        # For now, this is the same as download()
        # In the future, could add filtering by media_types
        return self.download(url)

    def _strategy_selenium_extraction(self, url: str) -> List[str]:
        """Extract media using Selenium headless browser."""
        if not self.options.use_headless_browser:
            return []

        urls = []
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from bs4 import BeautifulSoup

            self.log(self.tr("Starting headless browser for dynamic content..."))

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

            try:
                driver.get(url)
                # Wait for dynamic content? Simple sleep for now
                time.sleep(3)

                # Get rendered HTML
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Extract image and video tags from rendered source
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        urls.append(urljoin(url, src))

                for video in soup.find_all('video'):
                    src = video.get('src')
                    if src:
                        urls.append(urljoin(url, src))
                    for source in video.find_all('source'):
                        src = source.get('src')
                        if src:
                            urls.append(urljoin(url, src))

            finally:
                driver.quit()

        except Exception as e:
            logger.debug(f"Selenium extraction failed: {e}")

        return urls

    def _download_recursive(self, start_url: str, depth: int) -> DownloadResult:
        """
        Recursively crawl and download media.
        """
        visited = set()
        queue = [(start_url, 0)]
        results = DownloadResult(success=True, total_files=0, completed_files=0, failed_files=[], skipped_files=[])

        start_time = time.time()
        pages_crawled = 0

        while queue and pages_crawled < self.options.max_crawl_pages:
            if self.is_cancelled():
                break

            current_url, current_depth = queue.pop(0)

            if current_url in visited:
                continue
            visited.add(current_url)

            self.log(self.tr(f"Crawling: {current_url} (Depth: {current_depth})"))
            pages_crawled += 1

            # Analyze and download from current page
            # We temporarily set crawl_depth to 0 to avoid infinite recursion in analyze_page if we called download()
            # But wait, analyze_page doesn't call download().
            # We just need to extract links for the queue.

            analysis = self.analyze_page(current_url)

            # Add found media to total count logic
            self.total_files += analysis.total_items
            results.total_files += analysis.total_items

            # Download items found on this page
            for item in analysis.all_media:
                if self.is_cancelled(): break
                try:
                    subfolder = os.path.join(self.download_folder, item.media_type.value)
                    os.makedirs(subfolder, exist_ok=True)
                    filepath = os.path.join(subfolder, item.filename)
                    if self.download_file(item.url, filepath):
                        self.completed_files += 1
                        results.completed_files += 1
                    else:
                        self.failed_files.append(item.url)
                        results.failed_files.append(item.url)
                    self.report_global_progress()
                except Exception:
                    pass

            # If we haven't reached max depth, find links to other pages
            if current_depth < self.options.crawl_depth:
                new_links = self._extract_internal_links(current_url)
                for link in new_links:
                    if link not in visited:
                        queue.append((link, current_depth + 1))

        results.elapsed_seconds = time.time() - start_time
        return results

    def _extract_internal_links(self, url: str) -> List[str]:
        """Extract internal links from a page."""
        links = []
        try:
            response = self.safe_request(url)
            if response:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                base_domain = urlparse(url).netloc

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(url, href)
                    # Simple internal link check
                    if urlparse(full_url).netloc == base_domain:
                        links.append(full_url)
        except Exception:
            pass
        return links
