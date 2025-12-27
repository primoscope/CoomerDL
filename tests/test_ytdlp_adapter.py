"""
Unit tests for YtDlpDownloader (Universal yt-dlp adapter).
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from downloader.base import DownloadOptions
from downloader.ytdlp_adapter import YtDlpDownloader, YtDlpOptions


class TestYtDlpDownloaderInit:
    """Test YtDlpDownloader initialization."""
    
    def test_init_with_folder(self, download_folder):
        """Test basic initialization with download folder."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader.download_folder == download_folder
        assert downloader.ytdlp_options is not None
        assert isinstance(downloader.ytdlp_options, YtDlpOptions)
    
    def test_init_with_options(self, download_folder, download_options):
        """Test initialization with download options."""
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            options=download_options
        )
        
        assert downloader.options == download_options
    
    def test_init_with_ytdlp_options(self, download_folder):
        """Test initialization with custom yt-dlp options."""
        ytdlp_opts = YtDlpOptions(
            format_selector='bestaudio',
            merge_output_format='mkv',
            embed_thumbnail=False
        )
        
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        
        assert downloader.ytdlp_options.format_selector == 'bestaudio'
        assert downloader.ytdlp_options.merge_output_format == 'mkv'
        assert downloader.ytdlp_options.embed_thumbnail is False


class TestYtDlpDownloaderUrlSupport:
    """Test URL support detection."""
    
    def test_supports_youtube_url(self, download_folder):
        """Test that YouTube URLs are supported."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader.supports_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert downloader.supports_url("https://youtube.com/watch?v=test")
        assert downloader.supports_url("https://youtu.be/test")
    
    def test_supports_twitter_url(self, download_folder):
        """Test that Twitter/X URLs are supported."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader.supports_url("https://twitter.com/user/status/123")
        assert downloader.supports_url("https://x.com/user/status/123")
    
    def test_supports_reddit_url(self, download_folder):
        """Test that Reddit URLs are supported (handled by yt-dlp)."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        # Note: Reddit has a native downloader, but yt-dlp could also handle it
        # The domain check excludes native downloader domains
        assert downloader.supports_url("https://www.reddit.com/r/test/comments/123/")
    
    def test_rejects_native_downloader_domains(self, download_folder):
        """Test that URLs handled by native downloaders are rejected."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        # Coomer/Kemono domains
        assert not downloader.supports_url("https://coomer.su/onlyfans/user/test")
        assert not downloader.supports_url("https://kemono.su/patreon/user/test")
        assert not downloader.supports_url("https://coomer.party/test")
        
        # SimpCity
        assert not downloader.supports_url("https://simpcity.su/threads/test")
        assert not downloader.supports_url("https://simpcity.cr/forums/test")
        
        # Erome
        assert not downloader.supports_url("https://erome.com/a/test")
        
        # Bunkr
        assert not downloader.supports_url("https://bunkr.si/album/test")
        assert not downloader.supports_url("https://bunkr.site/v/test")
        
        # Jpg5
        assert not downloader.supports_url("https://jpg5.su/img/test")
    
    def test_rejects_non_http_urls(self, download_folder):
        """Test that non-HTTP URLs are rejected."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert not downloader.supports_url("ftp://example.com/file.mp4")
        assert not downloader.supports_url("file:///path/to/file.mp4")
        assert not downloader.supports_url("invalid-url")
    
    def test_supports_various_media_sites(self, download_folder):
        """Test support for various media sites."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        # Instagram
        assert downloader.supports_url("https://www.instagram.com/p/test/")
        
        # TikTok
        assert downloader.supports_url("https://www.tiktok.com/@user/video/123")
        
        # Twitch
        assert downloader.supports_url("https://www.twitch.tv/videos/123")
        assert downloader.supports_url("https://clips.twitch.tv/test")
        
        # Vimeo
        assert downloader.supports_url("https://vimeo.com/123456")


class TestYtDlpDownloaderSiteName:
    """Test site name reporting."""
    
    def test_get_site_name(self, download_folder):
        """Test that correct site name is returned."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader.get_site_name() == "Universal (yt-dlp)"


class TestYtDlpDownloaderOptions:
    """Test yt-dlp options building."""
    
    def test_default_options(self, download_folder):
        """Test default yt-dlp options."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        opts = downloader._build_ydl_opts()
        
        assert 'outtmpl' in opts
        assert download_folder in opts['outtmpl']
        assert opts['quiet'] is True
        assert opts['no_warnings'] is True
    
    def test_format_selector_best(self, download_folder):
        """Test 'best' format selector."""
        ytdlp_opts = YtDlpOptions(format_selector='best')
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts['format'] == 'bestvideo+bestaudio/best'
    
    def test_format_selector_audio(self, download_folder):
        """Test 'bestaudio' format selector."""
        ytdlp_opts = YtDlpOptions(format_selector='bestaudio')
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts['format'] == 'bestaudio/best'
        assert any(pp.get('key') == 'FFmpegExtractAudio' for pp in opts.get('postprocessors', []))
    
    def test_merge_output_format(self, download_folder):
        """Test merge output format setting."""
        ytdlp_opts = YtDlpOptions(merge_output_format='mkv')
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts['merge_output_format'] == 'mkv'
    
    def test_metadata_embedding(self, download_folder):
        """Test metadata embedding options."""
        ytdlp_opts = YtDlpOptions(embed_metadata=True)
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        postprocessors = opts.get('postprocessors', [])
        assert any(pp.get('key') == 'FFmpegMetadata' for pp in postprocessors)
    
    def test_thumbnail_embedding(self, download_folder):
        """Test thumbnail embedding options."""
        ytdlp_opts = YtDlpOptions(embed_thumbnail=True)
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts.get('writethumbnail') is True
        postprocessors = opts.get('postprocessors', [])
        assert any(pp.get('key') == 'EmbedThumbnail' for pp in postprocessors)
    
    def test_subtitle_options(self, download_folder):
        """Test subtitle download options."""
        ytdlp_opts = YtDlpOptions(
            download_subtitles=True,
            subtitle_languages='en,es'
        )
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts.get('writesubtitles') is True
        assert opts.get('subtitleslangs') == ['en', 'es']
    
    def test_cookies_from_browser(self, download_folder):
        """Test browser cookie extraction option."""
        ytdlp_opts = YtDlpOptions(cookies_from_browser='chrome')
        downloader = YtDlpDownloader(
            download_folder=download_folder,
            ytdlp_options=ytdlp_opts
        )
        opts = downloader._build_ydl_opts()
        
        assert opts.get('cookiesfrombrowser') == ('chrome',)


class TestYtDlpDownloaderRateLimit:
    """Test rate limit parsing."""
    
    def test_parse_rate_limit_megabytes(self, download_folder):
        """Test parsing MB rate limit."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader._parse_rate_limit('1M') == 1024 * 1024
        assert downloader._parse_rate_limit('2M') == 2 * 1024 * 1024
    
    def test_parse_rate_limit_kilobytes(self, download_folder):
        """Test parsing KB rate limit."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader._parse_rate_limit('500K') == 500 * 1024
    
    def test_parse_rate_limit_gigabytes(self, download_folder):
        """Test parsing GB rate limit."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader._parse_rate_limit('1G') == 1024 * 1024 * 1024
    
    def test_parse_rate_limit_numeric(self, download_folder):
        """Test parsing numeric rate limit (bytes)."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader._parse_rate_limit('1000000') == 1000000
    
    def test_parse_rate_limit_invalid(self, download_folder):
        """Test parsing invalid rate limit."""
        downloader = YtDlpDownloader(download_folder=download_folder)
        
        assert downloader._parse_rate_limit('invalid') is None
        assert downloader._parse_rate_limit('') is None
        assert downloader._parse_rate_limit(None) is None


class TestYtDlpDownloaderStaticMethods:
    """Test static methods."""
    
    def test_check_url_supported_youtube(self):
        """Test static URL support check for YouTube."""
        assert YtDlpDownloader.check_url_supported("https://www.youtube.com/watch?v=test")
    
    def test_check_url_supported_native_domain(self):
        """Test static URL support check rejects native domains."""
        assert not YtDlpDownloader.check_url_supported("https://coomer.su/test")
        assert not YtDlpDownloader.check_url_supported("https://kemono.su/test")
    
    def test_check_url_supported_invalid(self):
        """Test static URL support check for invalid URLs."""
        assert not YtDlpDownloader.check_url_supported("ftp://example.com")
        assert not YtDlpDownloader.check_url_supported("not-a-url")


class TestYtDlpOptions:
    """Test YtDlpOptions dataclass."""
    
    def test_default_values(self):
        """Test default option values."""
        opts = YtDlpOptions()
        
        assert opts.format_selector == 'best'
        assert opts.merge_output_format == 'mp4'
        assert opts.embed_thumbnail is True
        assert opts.embed_metadata is True
        assert opts.download_subtitles is False
        assert opts.subtitle_languages == 'en'
        assert opts.cookies_from_browser is None
        assert opts.ffmpeg_location is None
        assert opts.rate_limit is None
    
    def test_custom_values(self):
        """Test custom option values."""
        opts = YtDlpOptions(
            format_selector='bestaudio',
            merge_output_format='mkv',
            embed_thumbnail=False,
            embed_metadata=False,
            download_subtitles=True,
            subtitle_languages='en,es,fr',
            cookies_from_browser='firefox',
            rate_limit='5M'
        )
        
        assert opts.format_selector == 'bestaudio'
        assert opts.merge_output_format == 'mkv'
        assert opts.embed_thumbnail is False
        assert opts.embed_metadata is False
        assert opts.download_subtitles is True
        assert opts.subtitle_languages == 'en,es,fr'
        assert opts.cookies_from_browser == 'firefox'
        assert opts.rate_limit == '5M'
