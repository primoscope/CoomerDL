"""
Gallery Downloader - Universal gallery/image board downloader using gallery-dl.

Provides support for hundreds of image hosting sites through gallery-dl's extractor framework.
"""
import os
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Set
from urllib.parse import urlparse

from downloader.base import BaseDownloader, DownloadOptions, DownloadResult

logger = logging.getLogger(__name__)


@dataclass
class GalleryOptions:
    """Configuration options specific to gallery-dl downloads."""
    enabled: bool = True
    config_profile: Optional[str] = None
    write_metadata_json: bool = True
    write_urls: bool = False
    max_items: Optional[int] = None
    sleep_interval: Optional[float] = None  # Politeness delay
    cookies_file: Optional[str] = None


class GalleryDownloader(BaseDownloader):
    """
    Universal gallery downloader using gallery-dl library.
    
    Supports hundreds of image hosting sites through gallery-dl's extractor framework.
    Used for image boards, galleries, and sites not optimally handled by yt-dlp.
    """
    
    # Sites that have dedicated native downloaders - gallery-dl should not handle these
    NATIVE_DOWNLOADER_DOMAINS = {
        'coomer.su', 'coomer.party', 'coomer.st',
        'kemono.su', 'kemono.party', 'kemono.cr',
        'simpcity.su', 'simpcity.cr',
        'bunkr.si', 'bunkr.site', 'bunkr.ru', 'bunkr.to', 'bunkr.is',
    }
    
    # Sites that gallery-dl handles well (prioritize over yt-dlp)
    GALLERY_PREFERRED_DOMAINS = {
        'imgur.com', 'imgbox.com', 'imagebam.com',
        'deviantart.com', 'artstation.com', 'pixiv.net',
        'danbooru.donmai.us', 'gelbooru.com', 'rule34.xxx',
        'e621.net', 'furaffinity.net',
        'flickr.com', '500px.com',
        'tumblr.com', 'newgrounds.com',
        'hentai-foundry.com', 'paheal.net',
        'xhamster.com', 'pornhub.com',
        'gfycat.com', 'redgifs.com',
    }
    
    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        gallery_options: Optional[GalleryOptions] = None,
        **kwargs
    ):
        super().__init__(
            download_folder=download_folder,
            options=options,
            **kwargs
        )
        self.gallery_options = gallery_options or GalleryOptions()
        self._gallery_dl = None
        self._downloaded_urls: Set[str] = set()
        self._current_item = None
    
    def _get_gallery_dl(self):
        """Lazy import of gallery_dl module."""
        if self._gallery_dl is None:
            try:
                import gallery_dl
                self._gallery_dl = gallery_dl
            except ImportError:
                raise ImportError(
                    "gallery-dl is not installed. Please install it with: pip install gallery-dl"
                )
        return self._gallery_dl
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Lightweight check if this downloader can handle the URL.
        
        Checks against known gallery-dl supported domains and excludes
        domains that have native downloaders.
        
        Args:
            url: URL to check.
            
        Returns:
            True if URL might be supported by gallery-dl.
        """
        try:
            parsed = urlparse(url)
            
            # Basic sanity check
            if parsed.scheme not in ('http', 'https'):
                return False
            
            if not parsed.netloc:
                return False
            
            domain = parsed.netloc.lower().lstrip('www.')
            
            # Don't handle URLs that have native downloaders
            for native_domain in cls.NATIVE_DOWNLOADER_DOMAINS:
                if native_domain in domain:
                    return False
            
            # Prefer gallery-dl for known gallery sites
            for gallery_domain in cls.GALLERY_PREFERRED_DOMAINS:
                if gallery_domain in domain:
                    return True
            
            # For other URLs, try a quick extractor check
            return cls._check_extractor_support(url)
            
        except Exception:
            return False
    
    @classmethod
    def _check_extractor_support(cls, url: str) -> bool:
        """
        Check if gallery-dl has an extractor for this URL.
        
        This is a more thorough check that imports gallery-dl.
        """
        try:
            import gallery_dl
            from gallery_dl import extractor
            
            # Try to find an extractor for this URL
            extr = extractor.find(url)
            return extr is not None
            
        except ImportError:
            return False
        except Exception:
            return False
    
    def supports_url(self, url: str) -> bool:
        """Check if this downloader can handle the given URL."""
        return self.can_handle(url)
    
    def get_site_name(self) -> str:
        """Return the site name."""
        return "Gallery (gallery-dl)"
    
    def _build_config(self) -> Dict[str, Any]:
        """
        Build gallery-dl configuration dictionary.
        
        Returns:
            Configuration dictionary for gallery-dl.
        """
        config = {
            'extractor': {
                'base-directory': self.download_folder,
                'directory': ['{category}', '{subcategory|""}'],
                'filename': '{filename}.{extension}',
                'skip': True,  # Skip existing files
                'retries': self.options.max_retries,
                'timeout': self.options.timeout,
            },
            'output': {
                'mode': 'null',  # Suppress output, we handle progress ourselves
                'progress': False,
            },
        }
        
        # Apply gallery options
        if self.gallery_options.write_metadata_json:
            config['extractor']['postprocessors'] = [{
                'name': 'metadata',
                'mode': 'json',
            }]
        
        if self.gallery_options.sleep_interval:
            config['extractor']['sleep'] = self.gallery_options.sleep_interval
        
        if self.gallery_options.max_items:
            config['extractor']['range'] = f'1-{self.gallery_options.max_items}'
        
        if self.gallery_options.cookies_file:
            config['extractor']['cookies'] = self.gallery_options.cookies_file
        
        return config
    
    def download(self, url: str) -> DownloadResult:
        """
        Download media from the given URL using gallery-dl.
        
        Args:
            url: The URL to download from.
            
        Returns:
            DownloadResult with statistics about the download.
        """
        start_time = time.time()
        self.reset()
        self._downloaded_urls.clear()
        
        try:
            gallery_dl = self._get_gallery_dl()
            from gallery_dl import config, job, extractor
            
            self.log(self.tr(f"Starting gallery-dl download: {url}"))
            
            # Apply configuration
            config.clear()
            gdl_config = self._build_config()
            config.set((), 'extractor', gdl_config.get('extractor', {}))
            config.set((), 'output', gdl_config.get('output', {}))
            
            # First, resolve to get item count
            try:
                extr = extractor.find(url)
                if extr is None:
                    return DownloadResult(
                        success=False,
                        total_files=0,
                        completed_files=0,
                        error_message=f"No gallery-dl extractor found for URL: {url}"
                    )
                
                # Try to count items first (for progress)
                items = list(extr)
                self.total_files = len([i for i in items if i])
                self.log(self.tr(f"Found {self.total_files} item(s)"))
                
            except Exception as e:
                logger.warning(f"Could not pre-count items: {e}")
                self.total_files = 0  # Will update as we go
            
            if self.is_cancelled():
                return DownloadResult(
                    success=False,
                    total_files=self.total_files,
                    completed_files=0,
                    error_message="Download cancelled"
                )
            
            # Now download
            # Re-create extractor since we consumed it above
            download_job = job.DownloadJob(url)
            
            # Hook into the job for progress reporting
            original_handle_url = download_job.handle_url
            gallery_dl_module = self._gallery_dl  # Store reference for closure
            
            def hooked_handle_url(url_tuple):
                if self.is_cancelled():
                    raise gallery_dl_module.exception.StopExtraction("Cancelled by user")
                
                result = original_handle_url(url_tuple)
                
                # Report progress
                self.completed_files += 1
                self._current_item = url_tuple[0] if url_tuple else None
                
                self.report_progress(
                    downloaded=1,
                    total=1,
                    file_id=str(self.completed_files),
                    url=self._current_item,
                    status='Downloaded'
                )
                self.report_global_progress()
                
                return result
            
            download_job.handle_url = hooked_handle_url
            
            # Run the download job
            try:
                exit_code = download_job.run()
                
                # gallery-dl exit codes: 0 = success, 1 = some errors
                success = exit_code == 0 or self.completed_files > 0
                
            except Exception as e:
                if 'Cancelled' in str(e) or self.is_cancelled():
                    self.log(self.tr("Download cancelled by user"))
                    return DownloadResult(
                        success=False,
                        total_files=self.total_files,
                        completed_files=self.completed_files,
                        failed_files=self.failed_files,
                        skipped_files=self.skipped_files,
                        error_message="Download cancelled",
                        elapsed_seconds=time.time() - start_time
                    )
                raise
            
            return DownloadResult(
                success=success,
                total_files=self.total_files or self.completed_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                elapsed_seconds=time.time() - start_time
            )
            
        except ImportError as e:
            self.log(self.tr(f"Import error: {e}"))
            return DownloadResult(
                success=False,
                total_files=0,
                completed_files=0,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )
            
        except Exception as e:
            error_msg = str(e)
            self.log(self.tr(f"Download error: {error_msg}"))
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files + [url],
                error_message=error_msg,
                elapsed_seconds=time.time() - start_time
            )
    
    def analyze_gallery(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from URL without downloading.
        
        Useful for previewing gallery contents.
        
        Args:
            url: The URL to analyze.
            
        Returns:
            Dictionary with metadata, or None if extraction fails.
        """
        try:
            gallery_dl = self._get_gallery_dl()
            from gallery_dl import extractor
            
            extr = extractor.find(url)
            if extr is None:
                return None
            
            # Get basic info
            items = []
            for i, item in enumerate(extr):
                if i >= 10:  # Limit preview
                    break
                if item:
                    items.append({
                        'url': item[0] if isinstance(item, tuple) else str(item),
                    })
            
            return {
                'type': 'gallery',
                'category': getattr(extr, 'category', 'unknown'),
                'subcategory': getattr(extr, 'subcategory', ''),
                'item_count': len(items),
                'items_preview': items,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing gallery {url}: {e}")
            return None
    
    @classmethod
    def check_url_supported(cls, url: str) -> bool:
        """
        Static check if URL is potentially supported by gallery-dl.
        
        Args:
            url: URL to check.
            
        Returns:
            True if URL might be supported.
        """
        return cls.can_handle(url)
