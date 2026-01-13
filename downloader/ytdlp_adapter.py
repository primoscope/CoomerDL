"""
yt-dlp Adapter - Universal downloader using yt-dlp library.

Provides support for 1000+ sites by integrating yt-dlp as a Python library.
Used as a fallback when native downloaders don't support the URL.
"""
import os
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from downloader.base import BaseDownloader, DownloadOptions, DownloadResult

logger = logging.getLogger(__name__)


@dataclass
class YtDlpOptions:
    """Configuration options specific to yt-dlp downloads."""
    format_selector: str = 'best'  # 'best', 'bestvideo+bestaudio/best', 'bestaudio'
    merge_output_format: str = 'mp4'  # mp4, mkv, webm
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    download_subtitles: bool = False
    subtitle_languages: str = 'en'  # comma-separated language codes
    cookies_from_browser: Optional[str] = None  # 'chrome', 'firefox', etc.
    ffmpeg_location: Optional[str] = None
    rate_limit: Optional[str] = None  # e.g., '1M' for 1MB/s


class YtDlpDownloader(BaseDownloader):
    """
    Universal downloader using yt-dlp library.

    Supports 1000+ sites through yt-dlp's extractor framework.
    Should be used as a fallback when native downloaders don't support the URL.
    """

    # Sites that have dedicated native downloaders - yt-dlp should not handle these
    NATIVE_DOWNLOADER_DOMAINS = {
        'coomer.su', 'coomer.party', 'coomer.st',
        'kemono.su', 'kemono.party', 'kemono.cr',
        'simpcity.su', 'simpcity.cr',
        'erome.com',
        'bunkr.si', 'bunkr.site', 'bunkr.ru', 'bunkr.to', 'bunkr.is',
        'jpg5.su',
    }

    # Configuration constants
    PLAYLIST_PREVIEW_LIMIT = 10  # Max items to show in playlist preview
    DESCRIPTION_TRUNCATE_LENGTH = 500  # Max characters for description preview

    def __init__(
        self,
        download_folder: str,
        options: Optional[DownloadOptions] = None,
        ytdlp_options: Optional[YtDlpOptions] = None,
        **kwargs
    ):
        super().__init__(
            download_folder=download_folder,
            options=options,
            **kwargs
        )
        self.ytdlp_options = ytdlp_options or YtDlpOptions()
        self._yt_dlp = None
        self._current_filename = None
        self._download_start_time = None

    def _get_yt_dlp(self):
        """Lazy import of yt_dlp module."""
        if self._yt_dlp is None:
            try:
                import yt_dlp
                self._yt_dlp = yt_dlp
            except ImportError:
                raise ImportError(
                    "yt-dlp is not installed. Please install it with: pip install yt-dlp"
                )
        return self._yt_dlp

    def supports_url(self, url: str) -> bool:
        """
        Check if this downloader can handle the given URL.

        Returns True for URLs that:
        1. Are not handled by native downloaders
        2. Are potentially supported by yt-dlp

        Note: We don't do expensive extractor checks here.
        The factory will use this as a fallback.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().lstrip('www.')

            # Don't handle URLs that have native downloaders
            for native_domain in self.NATIVE_DOWNLOADER_DOMAINS:
                if native_domain in domain:
                    return False

            # Accept any http/https URL as potentially supported
            return parsed.scheme in ('http', 'https')

        except Exception:
            return False

    def get_site_name(self) -> str:
        """Return the site name."""
        return "Universal (yt-dlp)"

    def _build_ydl_opts(self) -> Dict[str, Any]:
        """
        Build yt-dlp options dictionary from our configuration.

        Returns:
            Dictionary of yt-dlp options.
        """
        # Build output template
        outtmpl = os.path.join(
            self.download_folder,
            '%(uploader|Unknown)s',
            '%(title)s [%(id)s].%(ext)s'
        )

        opts = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'progress_hooks': [self._progress_hook],
            'postprocessor_hooks': [self._postprocessor_hook],
            'ignoreerrors': False,
            'retries': self.options.max_retries,
            'socket_timeout': self.options.timeout,
            'nocheckcertificate': True,
        }

        # Format selection
        format_selector = self.ytdlp_options.format_selector
        if format_selector == 'best':
            opts['format'] = 'bestvideo+bestaudio/best'
        elif format_selector == 'bestaudio':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opts['format'] = format_selector

        # Merge output format (for video+audio merging)
        if self.ytdlp_options.merge_output_format:
            opts['merge_output_format'] = self.ytdlp_options.merge_output_format

        # Metadata and thumbnails
        postprocessors = opts.get('postprocessors', [])

        if self.ytdlp_options.embed_metadata:
            postprocessors.append({'key': 'FFmpegMetadata'})

        if self.ytdlp_options.embed_thumbnail:
            opts['writethumbnail'] = True
            postprocessors.append({
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            })

        if postprocessors:
            opts['postprocessors'] = postprocessors

        # Subtitles
        if self.ytdlp_options.download_subtitles:
            opts['writesubtitles'] = True
            opts['subtitleslangs'] = self.ytdlp_options.subtitle_languages.split(',')

        # Cookie import from browser
        if self.ytdlp_options.cookies_from_browser:
            opts['cookiesfrombrowser'] = (self.ytdlp_options.cookies_from_browser,)

        # FFmpeg location
        if self.ytdlp_options.ffmpeg_location:
            opts['ffmpeg_location'] = self.ytdlp_options.ffmpeg_location

        # Rate limiting
        if self.ytdlp_options.rate_limit:
            opts['ratelimit'] = self._parse_rate_limit(self.ytdlp_options.rate_limit)

        return opts

    def _parse_rate_limit(self, rate_str: str) -> Optional[int]:
        """Parse rate limit string like '1M' to bytes per second."""
        if not rate_str:
            return None

        try:
            rate_str = rate_str.upper().strip()
            multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3}

            for suffix, multiplier in multipliers.items():
                if rate_str.endswith(suffix):
                    return int(float(rate_str[:-1]) * multiplier)

            return int(rate_str)
        except (ValueError, TypeError):
            return None

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Progress hook called by yt-dlp during download.

        Translates yt-dlp's progress dictionary to our reporting format.
        """
        # Check for cancellation
        if self.is_cancelled():
            raise self._get_yt_dlp().utils.DownloadCancelled("Download cancelled by user")

        status = d.get('status', '')

        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            filename = d.get('filename', '')

            self._current_filename = os.path.basename(filename) if filename else None

            # Report progress
            self.report_progress(
                downloaded=downloaded,
                total=total,
                speed=speed,
                eta=eta,
                filename=self._current_filename,
                status='Downloading'
            )

        elif status == 'finished':
            filename = d.get('filename', '')
            self._current_filename = os.path.basename(filename) if filename else None
            self.log(self.tr(f"Download finished: {self._current_filename}"))

        elif status == 'error':
            error_msg = d.get('error', 'Unknown error')
            self.log(self.tr(f"Download error: {error_msg}"))

    def _postprocessor_hook(self, d: Dict[str, Any]) -> None:
        """
        Postprocessor hook called by yt-dlp during post-processing.
        """
        # Check for cancellation
        if self.is_cancelled():
            raise self._get_yt_dlp().utils.DownloadCancelled("Post-processing cancelled")

        status = d.get('status', '')
        postprocessor = d.get('postprocessor', '')

        if status == 'started':
            self.log(self.tr(f"Processing: {postprocessor}"))
            self.report_progress(
                downloaded=0,
                total=0,
                status=f'Processing: {postprocessor}'
            )
        elif status == 'finished':
            self.log(self.tr(f"Finished: {postprocessor}"))

    def download(self, url: str) -> DownloadResult:
        """
        Download media from the given URL using yt-dlp.

        Args:
            url: The URL to download from.

        Returns:
            DownloadResult with statistics about the download.
        """
        start_time = time.time()
        self.reset()
        self._download_start_time = start_time

        try:
            yt_dlp = self._get_yt_dlp()

            self.log(self.tr(f"Starting yt-dlp download: {url}"))

            # Build options
            ydl_opts = self._build_ydl_opts()

            # Create downloader and extract info first
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract info to get file count
                    info = ydl.extract_info(url, download=False)

                    if info is None:
                        return DownloadResult(
                            success=False,
                            total_files=0,
                            completed_files=0,
                            error_message="Could not extract info from URL"
                        )

                    # Count entries (playlist) or single video
                    if 'entries' in info:
                        entries = list(info['entries'])
                        self.total_files = len([e for e in entries if e is not None])
                    else:
                        self.total_files = 1

                    self.log(self.tr(f"Found {self.total_files} media item(s)"))

                    # Now actually download
                    if self.is_cancelled():
                        return DownloadResult(
                            success=False,
                            total_files=self.total_files,
                            completed_files=0,
                            error_message="Download cancelled"
                        )

                    ydl.download([url])
                    self.completed_files = self.total_files

                except yt_dlp.utils.DownloadCancelled:
                    self.log(self.tr("Download was cancelled"))
                    return DownloadResult(
                        success=False,
                        total_files=self.total_files,
                        completed_files=self.completed_files,
                        error_message="Download cancelled by user",
                        elapsed_seconds=time.time() - start_time
                    )

                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    self.log(self.tr(f"Download error: {error_msg}"))
                    self.failed_files.append(url)
                    return DownloadResult(
                        success=False,
                        total_files=self.total_files,
                        completed_files=self.completed_files,
                        failed_files=self.failed_files,
                        error_message=error_msg,
                        elapsed_seconds=time.time() - start_time
                    )

            success = self.completed_files > 0 and not self.is_cancelled()

            return DownloadResult(
                success=success,
                total_files=self.total_files,
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
            self.log(self.tr(f"Unexpected error: {e}"))
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )

    def analyze_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from URL without downloading.

        Useful for previewing what will be downloaded.

        Args:
            url: The URL to analyze.

        Returns:
            Dictionary with metadata, or None if extraction fails.
        """
        try:
            yt_dlp = self._get_yt_dlp()

            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info is None:
                    return None

                # Handle playlists
                if 'entries' in info:
                    entries = list(info['entries'])
                    valid_entries = [e for e in entries if e is not None]
                    return {
                        'type': 'playlist',
                        'title': info.get('title', 'Unknown Playlist'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'item_count': len(valid_entries),
                        'items': [
                            {
                                'title': e.get('title', 'Unknown'),
                                'duration': e.get('duration'),
                                'thumbnail': e.get('thumbnail'),
                            }
                            for e in valid_entries[:self.PLAYLIST_PREVIEW_LIMIT]
                        ]
                    }
                else:
                    # Single video/media
                    description = info.get('description', '')
                    return {
                        'type': 'video',
                        'title': info.get('title', 'Unknown'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'duration': info.get('duration'),
                        'thumbnail': info.get('thumbnail'),
                        'description': description[:self.DESCRIPTION_TRUNCATE_LENGTH] if description else '',
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'upload_date': info.get('upload_date'),
                        'formats_available': len(info.get('formats', [])),
                        'estimated_filesize': self._estimate_filesize(info),
                    }

        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {e}")
            return None

    def _estimate_filesize(self, info: Dict[str, Any]) -> Optional[int]:
        """Estimate file size from format info."""
        try:
            formats = info.get('formats', [])
            if not formats:
                return None

            # Find best format and get its filesize
            for fmt in reversed(formats):
                if fmt.get('filesize'):
                    return fmt['filesize']
                if fmt.get('filesize_approx'):
                    return fmt['filesize_approx']

            return None
        except Exception:
            return None

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Lightweight class-level check if URL is potentially supported by yt-dlp.
        
        This is used by the factory for efficient routing without instantiation.
        
        Args:
            url: URL to check.
            
        Returns:
            True if URL might be supported.
        """
        try:
            parsed = urlparse(url)

            # Basic sanity check
            if parsed.scheme not in ('http', 'https'):
                return False

            if not parsed.netloc:
                return False

            # Check against native downloader domains
            domain = parsed.netloc.lower().lstrip('www.')
            for native_domain in cls.NATIVE_DOWNLOADER_DOMAINS:
                if native_domain in domain:
                    return False

            return True

        except Exception:
            return False

    @classmethod
    def check_url_supported(cls, url: str) -> bool:
        """
        Static check if URL is potentially supported by yt-dlp.

        This is a lightweight check that doesn't import yt-dlp.
        Alias for can_handle() for backward compatibility.

        Args:
            url: URL to check.

        Returns:
            True if URL might be supported.
        """
        return cls.can_handle(url)
