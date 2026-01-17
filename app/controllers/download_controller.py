"""
Download Controller - Coordinates download operations across different platforms.

This controller extracts download coordination logic from the UI layer,
handling URL routing, downloader setup, and download execution.
"""

from __future__ import annotations

import datetime
import re
import threading
from typing import Optional, Callable, Dict, Any
from urllib.parse import ParseResult, parse_qs, urlparse

from downloader.bunkr import BunkrDownloader
from downloader.downloader import Downloader
from downloader.erome import EromeDownloader
from downloader.simpcity import SimpCity
from downloader.jpg5 import Jpg5Downloader


def extract_ck_parameters(url: ParseResult) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Get the service, user and post id from the url if they exist
    """
    match = re.search(r"/(?P<service>[^/?]+)(/user/(?P<user>[^/?]+)(/post/(?P<post>[^/?]+))?)?", url.path)
    if match:
        [site, service, post] = match.group("service", "user", "post")
        return site, service, post
    else:
        return None, None, None


def extract_ck_query(url: ParseResult) -> tuple[Optional[str], int]:
    """
    Try to obtain the query and offset from the url if they exist
    """
    # This is kinda contrived but query parameters are awful to get right
    query = parse_qs(url.query)
    q = query.get("q")[0] if query.get("q") is not None and len(query.get("q")) > 0 else "0"
    o = query.get("o")[0] if query.get("o") is not None and len(query.get("o")) > 0 else "0"

    return q, int(o) if str.isdigit(o) else 0


class DownloadController:
    """
    Controller for managing download operations.
    
    This class coordinates download operations across different platforms,
    handling URL routing, downloader setup, and execution while remaining
    independent of the UI layer through callbacks.
    """
    
    def __init__(
        self,
        download_folder: str,
        settings: Dict[str, Any],
        max_downloads: int,
        # UI Callbacks
        log_callback: Callable[[str], None],
        update_progress_callback: Callable[[str, int, int], None],
        update_global_progress_callback: Callable[[int, int], None],
        enable_widgets_callback: Callable[[], None],
        export_logs_callback: Callable[[], None],
        # Checkbox state getters
        get_download_images: Callable[[], bool],
        get_download_videos: Callable[[], bool],
        get_download_compressed: Callable[[], bool],
        get_download_documents: Callable[[], bool],
        # Translation function
        tr: Callable[[str], str],
        # Progress manager (for jpg5)
        progress_manager: Any = None,
        # Root reference (for erome)
        root: Any = None
    ):
        """
        Initialize the download controller.
        
        Args:
            download_folder: Path to download folder
            settings: Application settings dictionary
            max_downloads: Maximum concurrent downloads
            log_callback: Callback for logging messages
            update_progress_callback: Callback for updating progress
            update_global_progress_callback: Callback for global progress
            enable_widgets_callback: Callback to enable UI widgets
            export_logs_callback: Callback to export logs
            get_download_images: Function to get download images checkbox state
            get_download_videos: Function to get download videos checkbox state
            get_download_compressed: Function to get download compressed checkbox state
            get_download_documents: Function to get download documents checkbox state
            tr: Translation function
            progress_manager: Progress manager instance (for jpg5)
            root: Root widget reference (for erome)
        """
        self.download_folder = download_folder
        self.settings = settings
        self.max_downloads = max_downloads
        
        # Callbacks
        self.log_callback = log_callback
        self.update_progress_callback = update_progress_callback
        self.update_global_progress_callback = update_global_progress_callback
        self.enable_widgets_callback = enable_widgets_callback
        self.export_logs_callback = export_logs_callback
        
        # Checkbox state getters
        self.get_download_images = get_download_images
        self.get_download_videos = get_download_videos
        self.get_download_compressed = get_download_compressed
        self.get_download_documents = get_download_documents
        
        # Translation
        self.tr = tr
        
        # Additional dependencies
        self.progress_manager = progress_manager
        self.root = root
        
        # State
        self.active_downloader: Optional[Any] = None
        self.erome_downloader: Optional[EromeDownloader] = None
        self.bunkr_downloader: Optional[BunkrDownloader] = None
        self.general_downloader: Optional[Downloader] = None
        self.simpcity_downloader: Optional[SimpCity] = None
    
    def get_active_downloader(self) -> Optional[Any]:
        """Get the currently active downloader instance."""
        return self.active_downloader
    
    def setup_erome_downloader(self, is_profile_download: bool = False) -> None:
        """Setup Erome downloader with current settings."""
        self.erome_downloader = EromeDownloader(
            root=self.root,
            enable_widgets_callback=self.enable_widgets_callback,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Referer': 'https://www.erome.com/'
            },
            log_callback=self.log_callback,
            update_progress_callback=self.update_progress_callback,
            update_global_progress_callback=self.update_global_progress_callback,
            download_images=self.get_download_images(),
            download_videos=self.get_download_videos(),
            is_profile_download=is_profile_download,
            max_workers=self.max_downloads,
            tr=self.tr
        )
    
    def setup_simpcity_downloader(self) -> None:
        """Setup SimpCity downloader with current settings."""
        self.simpcity_downloader = SimpCity(
            download_folder=self.download_folder,
            log_callback=self.log_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            update_progress_callback=self.update_progress_callback,
            update_global_progress_callback=self.update_global_progress_callback,
            tr=self.tr
        )
    
    def setup_bunkr_downloader(self) -> None:
        """Setup Bunkr downloader with current settings."""
        self.bunkr_downloader = BunkrDownloader(
            download_folder=self.download_folder,
            log_callback=self.log_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            update_progress_callback=self.update_progress_callback,
            update_global_progress_callback=self.update_global_progress_callback,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Referer': 'https://bunkr.site/',
            },
            max_workers=self.max_downloads
        )
    
    def setup_general_downloader(self) -> None:
        """Setup general downloader (Coomer/Kemono) with current settings."""
        # Load network settings
        network_settings = self.settings.get('network', {})
        proxy_type = network_settings.get('proxy_type', 'none')
        proxy_url = network_settings.get('proxy_url', '')
        user_agent = network_settings.get('user_agent', None)
        
        self.general_downloader = Downloader(
            download_folder=self.download_folder,
            log_callback=self.log_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            update_progress_callback=self.update_progress_callback,
            update_global_progress_callback=self.update_global_progress_callback,
            headers={
                'User-Agent': user_agent or 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Referer': 'https://coomer.st/',
                "Accept": "text/css"
            },
            download_images=self.get_download_images(),
            download_videos=self.get_download_videos(),
            download_compressed=self.get_download_compressed(),
            tr=self.tr,
            max_workers=self.max_downloads,
            folder_structure=self.settings.get('folder_structure', 'default'),
            proxy_type=proxy_type,
            proxy_url=proxy_url,
            user_agent=user_agent
        )
        self.general_downloader.file_naming_mode = self.settings.get('file_naming_mode', 0)
    
    def setup_jpg5_downloader(self, url: str) -> None:
        """Setup Jpg5 downloader with current settings."""
        self.active_downloader = Jpg5Downloader(
            url=url,
            carpeta_destino=self.download_folder,
            log_callback=self.log_callback,
            tr=self.tr,
            progress_manager=self.progress_manager,
            max_workers=self.max_downloads
        )
    
    def wrapped_download(self, download_method: Callable[..., Any], *args: Any) -> None:
        """
        Wrapper for legacy download methods.
        
        Executes the download method and ensures cleanup happens.
        """
        try:
            download_method(*args)
        finally:
            self.active_downloader = None
            self.enable_widgets_callback()
            self.export_logs_callback()
    
    def wrapped_base_download(self, downloader: Any, url: str) -> None:
        """
        Wrapper for BaseDownloader-compatible downloaders.
        
        Executes download and logs results.
        """
        try:
            result = downloader.download(url)
            if result.success:
                self.log_callback(self.tr(f"Descarga completada: {result.completed_files} archivos"))
            else:
                self.log_callback(self.tr(f"Descarga fallida: {result.error_message}"))
        except Exception as e:
            self.log_callback(self.tr(f"Error durante la descarga: {e}"))
        finally:
            self.active_downloader = None
            self.enable_widgets_callback()
            self.export_logs_callback()
    
    def start_ck_profile_download(
        self, 
        site: str, 
        service: str, 
        user: str, 
        query: Optional[str], 
        download_all: bool, 
        initial_offset: int
    ) -> Any:
        """Start Coomer/Kemono profile download."""
        download_info = self.active_downloader.download_media(
            site, user, service, query=query, download_all=download_all, initial_offset=initial_offset
        )
        if download_info:
            self.log_callback(f"Download info: {download_info}")
        return download_info
    
    def start_ck_post_download(self, site: str, service: str, user: str, post: str) -> Any:
        """Start Coomer/Kemono single post download."""
        download_info = self.active_downloader.download_single_post(site, post, service, user)
        if download_info:
            self.log_callback(f"Download info: {download_info}")
        return download_info
    
    def process_url(
        self, 
        url: str,
        on_download_button_callback: Callable[[str], None],
        on_cancel_button_callback: Callable[[str], None]
    ) -> Optional[threading.Thread]:
        """
        Process a single URL and start the appropriate download.
        
        This is the main entry point for the controller. It:
        1. Routes the URL to the appropriate downloader
        2. Sets up the downloader with current settings
        3. Creates and returns a download thread (but doesn't start it)
        
        Args:
            url: The URL to download
            on_download_button_callback: Callback to update download button state
            on_cancel_button_callback: Callback to update cancel button state
            
        Returns:
            Threading.Thread ready to start, or None if URL is invalid
        """
        if not self.download_folder:
            self.log_callback(self.tr("Por favor, selecciona una carpeta de descarga."))
            return None
        
        # Update button states
        on_download_button_callback("disabled")
        on_cancel_button_callback("normal")
        
        download_all = True
        parsed_url = urlparse(url)
        download_thread = None
        
        # Route to appropriate downloader
        if "erome.com" in url:
            download_thread = self._handle_erome(url)
        
        elif re.search(r"https?://([a-z0-9-]+\.)?bunkr\.[a-z]{2,}", url):
            download_thread = self._handle_bunkr(url)
        
        elif parsed_url.netloc in ["coomer.st", "kemono.cr"]:
            download_thread = self._handle_coomer_kemono(url, parsed_url, download_all)
            if download_thread is None:
                # Invalid URL - buttons already updated by handler
                return None
        
        elif "simpcity.cr" in url:
            download_thread = self._handle_simpcity(url)
        
        elif "jpg5.su" in url:
            download_thread = self._handle_jpg5(url)
        
        else:
            # Universal fallback
            download_thread = self._handle_universal(url)
            if download_thread is None:
                # No compatible downloader
                on_download_button_callback("normal")
                on_cancel_button_callback("disabled")
                return None
        
        return download_thread
    
    def _handle_erome(self, url: str) -> threading.Thread:
        """Handle Erome URLs."""
        self.log_callback(self.tr("Descargando Erome"))
        is_profile_download = "/a/" not in url
        self.setup_erome_downloader(is_profile_download=is_profile_download)
        self.active_downloader = self.erome_downloader
        
        if "/a/" in url:
            self.log_callback(self.tr("URL del álbum"))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(
                    self.active_downloader.process_album_page,
                    url,
                    self.download_folder,
                    self.get_download_images(),
                    self.get_download_videos()
                )
            )
        else:
            self.log_callback(self.tr("URL del perfil"))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(
                    self.active_downloader.process_profile_page,
                    url,
                    self.download_folder,
                    self.get_download_images(),
                    self.get_download_videos()
                )
            )
        
        return download_thread
    
    def _handle_bunkr(self, url: str) -> threading.Thread:
        """Handle Bunkr URLs."""
        self.log_callback(self.tr("Descargando Bunkr"))
        self.setup_bunkr_downloader()
        self.active_downloader = self.bunkr_downloader
        
        # Si la URL contiene "/v/", "/i/" o "/f/", la tratamos como un post individual.
        if any(sub in url for sub in ["/v/", "/i/", "/f/"]):
            self.log_callback(self.tr("URL del post"))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(self.bunkr_downloader.descargar_post_bunkr, url)
            )
        else:
            self.log_callback(self.tr("URL del perfil"))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(self.bunkr_downloader.descargar_perfil_bunkr, url)
            )
        
        return download_thread
    
    def _handle_coomer_kemono(
        self, 
        url: str, 
        parsed_url: ParseResult, 
        download_all: bool
    ) -> Optional[threading.Thread]:
        """Handle Coomer/Kemono URLs."""
        self.log_callback(self.tr("Iniciando descarga..."))
        self.setup_general_downloader()
        self.active_downloader = self.general_downloader
        
        site = f"{parsed_url.netloc}"
        service, user, post = extract_ck_parameters(parsed_url)
        
        if service is None or user is None:
            if service is None:
                self.log_callback(self.tr("No se pudo extraer el servicio."))
            else:
                self.log_callback(self.tr("No se pudo extraer el ID del usuario."))
            
            self.log_callback(self.tr("URL no válida"))
            return None
        
        self.log_callback(self.tr("Servicio extraído: {service} del sitio: {site}", service=service, site=site))
        
        if post is not None:
            self.log_callback(self.tr("Descargando post único..."))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(self.start_ck_post_download, site, service, user, post)
            )
        else:
            query, offset = extract_ck_query(parsed_url)
            self.log_callback(self.tr("Descargando todo el contenido del usuario..."))
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(self.start_ck_profile_download, site, service, user, query, download_all, offset)
            )
        
        return download_thread
    
    def _handle_simpcity(self, url: str) -> threading.Thread:
        """Handle SimpCity URLs."""
        self.log_callback(self.tr("Descargando SimpCity"))
        
        # Try using DownloaderFactory for simpcity
        from downloader.factory import DownloaderFactory
        from downloader.base import DownloadOptions
        
        # Create options from UI checkboxes
        options = DownloadOptions(
            download_images=self.get_download_images(),
            download_videos=self.get_download_videos(),
            download_compressed=self.get_download_compressed()
        )
        
        # Try to get downloader from factory
        downloader = DownloaderFactory.get_downloader(
            url=url,
            download_folder=self.download_folder,
            options=options,
            log_callback=self.log_callback,
            progress_callback=self.update_progress_callback,
            global_progress_callback=self.update_global_progress_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            tr=self.tr
        )
        
        if downloader:
            # Successfully got a downloader
            downloader_name = downloader.__class__.__name__
            self.log_callback(self.tr(f"Using {downloader_name} for this URL"))
            self.active_downloader = downloader
            download_thread = threading.Thread(
                target=self.wrapped_base_download,
                args=(downloader, url)
            )
        else:
            # Fallback to legacy method if factory doesn't work
            self.setup_simpcity_downloader()
            self.active_downloader = self.simpcity_downloader
            download_thread = threading.Thread(
                target=self.wrapped_download,
                args=(self.active_downloader.download_images_from_simpcity, url)
            )
        
        return download_thread
    
    def _handle_jpg5(self, url: str) -> threading.Thread:
        """Handle Jpg5 URLs."""
        self.log_callback(self.tr("Descargando desde Jpg5"))
        self.setup_jpg5_downloader(url)
        
        # Usar wrapped_download para manejar la descarga
        download_thread = threading.Thread(
            target=self.wrapped_download,
            args=(self.active_downloader.descargar_imagenes,)
        )
        
        return download_thread
    
    def _handle_universal(self, url: str) -> Optional[threading.Thread]:
        """Handle universal URLs using yt-dlp and DownloaderFactory."""
        self.log_callback(self.tr("Detecting downloader for URL..."))
        
        from downloader.factory import DownloaderFactory
        from downloader.base import DownloadOptions
        from downloader.ytdlp_adapter import YtDlpOptions
        
        # Create DownloadOptions from UI checkboxes
        options = DownloadOptions(
            download_images=self.get_download_images(),
            download_videos=self.get_download_videos(),
            download_compressed=self.get_download_compressed(),
            download_documents=self.get_download_documents(),
            max_retries=self.settings.get('max_retries', 3),
            retry_interval=self.settings.get('retry_interval', 2.0)
        )
        
        # Create YtDlpOptions from settings
        ytdlp_options = YtDlpOptions(
            format_selector=self.settings.get('ytdlp_format', 'best'),
            merge_output_format=self.settings.get('ytdlp_container', 'mp4'),
            embed_thumbnail=self.settings.get('ytdlp_embed_thumbnail', True),
            embed_metadata=self.settings.get('ytdlp_embed_metadata', True),
            download_subtitles=self.settings.get('ytdlp_download_subtitles', False),
            subtitle_languages=self.settings.get('ytdlp_subtitle_languages', 'en'),
            cookies_from_browser=self.settings.get('ytdlp_cookies_browser') if self.settings.get('ytdlp_cookies_browser') not in [None, 'None'] else None
        )
        
        # Try to get downloader from factory
        downloader = DownloaderFactory.get_downloader(
            url=url,
            download_folder=self.download_folder,
            options=options,
            ytdlp_options=ytdlp_options,
            log_callback=self.log_callback,
            progress_callback=self.update_progress_callback,
            global_progress_callback=self.update_global_progress_callback,
            enable_widgets_callback=self.enable_widgets_callback,
            tr=self.tr
        )
        
        if downloader:
            # Successfully got a downloader
            downloader_name = downloader.__class__.__name__
            self.log_callback(self.tr(f"Using {downloader_name} for this URL"))
            self.active_downloader = downloader
            download_thread = threading.Thread(
                target=self.wrapped_base_download,
                args=(downloader, url)
            )
            return download_thread
        else:
            # No downloader available
            self.log_callback(self.tr("No compatible downloader found for this URL"))
            return None
