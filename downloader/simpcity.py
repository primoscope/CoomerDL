import os
import json
import re
import queue
import threading
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import cloudscraper
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from downloader.base import BaseDownloader, DownloadOptions, DownloadResult
from downloader.factory import DownloaderFactory

@DownloaderFactory.register
class SimpCity(BaseDownloader):
    """SimpCity downloader - inherits from BaseDownloader."""
    
    def __init__(
        self, 
        download_folder: str, 
        options: Optional[DownloadOptions] = None,
        log_callback=None, 
        enable_widgets_callback=None, 
        progress_callback=None,
        global_progress_callback=None,
        tr=None,
        max_workers=5
    ):
        # Call parent constructor
        super().__init__(
            download_folder=download_folder,
            options=options,
            log_callback=log_callback,
            progress_callback=progress_callback,
            global_progress_callback=global_progress_callback,
            enable_widgets_callback=enable_widgets_callback,
            tr=tr
        )
        
        self.max_workers = max_workers
        self.descargadas = set()
        self.download_queue = queue.Queue()
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        
        # For backward compatibility with old UI callback signature
        self.update_progress_callback = progress_callback
        self.update_global_progress_callback = global_progress_callback

        # Selectors from original crawler
        self.title_selector = "h1[class=p-title-value]"
        self.posts_selector = "div[class*=message-main]"
        self.post_content_selector = "div[class*=message-userContent]"
        self.images_selector = "img[class*=bbImage]"
        self.videos_selector = "video source"
        self.iframe_selector = "iframe[class=saint-iframe]"
        self.attachments_block_selector = "section[class=message-attachments]"
        self.attachments_selector = "a"
        self.next_page_selector = "a[class*=pageNav-jump--next]"
        self.cookies_path = "resources/config/cookies/simpcity.json"
        self.set_cookies()
    
    def supports_url(self, url: str) -> bool:
        """Check if this downloader can handle SimpCity URLs."""
        return "simpcity.cr" in url.lower() or "simpcity.su" in url.lower()
    
    def get_site_name(self) -> str:
        """Return the site name."""
        return "SimpCity"
    
    def download(self, url: str) -> DownloadResult:
        """
        Main download method following BaseDownloader interface.
        
        Args:
            url: The SimpCity thread URL to download
            
        Returns:
            DownloadResult with statistics
        """
        start_time = time.time()
        self.reset()
        
        try:
            self.download_images_from_simpcity(url)
            
            return DownloadResult(
                success=not self.is_cancelled() and len(self.failed_files) == 0,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                elapsed_seconds=time.time() - start_time
            )
        except Exception as e:
            self.log(self.tr(f"Error during download: {e}"))
            return DownloadResult(
                success=False,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                skipped_files=self.skipped_files,
                error_message=str(e),
                elapsed_seconds=time.time() - start_time
            )

    def sanitize_folder_name(self, name):
        return re.sub(r'[<>:"/\\|?*]', '_', name)
    
    def set_cookies(self):
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)

            if isinstance(cookies, dict):
                cookies = [cookies]

            for c in cookies:
                if isinstance(c, dict) and "name" in c and "value" in c:
                    self.scraper.cookies.set(c["name"], c["value"])

    def fetch_page(self, url):
        try:
            response = self.scraper.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                self.log(self.tr(f"Error: {response.status_code} al acceder a {url}"))
                return None
        except Exception as e:
            self.log(self.tr(f"Error al acceder a {url}: {e}"))
            return None

    def save_file(self, file_url, path):
        if self.is_cancelled():
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        response = self.scraper.get(file_url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    if self.is_cancelled():
                        return
                    file.write(chunk)
            self.log(self.tr(f"Archivo descargado: {path}"))
            self.completed_files += 1
            self.report_global_progress()
        else:
            self.log(self.tr(f"Error al descargar {file_url}: {response.status_code}"))
            self.failed_files.append(file_url)

    def process_post(self, post_content, download_folder):
        if self.is_cancelled():
            return
        # Procesar imágenes
        images = post_content.select(self.images_selector)
        for img in images:
            if self.is_cancelled():
                return
            src = img.get('src')
            if src:
                file_name = os.path.basename(urlparse(src).path)
                file_path = os.path.join(download_folder, file_name)
                self.total_files += 1
                self.save_file(src, file_path)

        # Procesar videos
        videos = post_content.select(self.videos_selector)
        for video in videos:
            if self.is_cancelled():
                return
            src = video.get('src')
            if src:
                file_name = os.path.basename(urlparse(src).path)
                file_path = os.path.join(download_folder, file_name)
                self.total_files += 1
                self.save_file(src, file_path)

        # Procesar archivos adjuntos
        attachments_block = post_content.select_one(self.attachments_block_selector)
        if attachments_block:
            attachments = attachments_block.select(self.attachments_selector)
            for attachment in attachments:
                if self.is_cancelled():
                    return
                href = attachment.get('href')
                if href:
                    file_name = os.path.basename(urlparse(href).path)
                    file_path = os.path.join(download_folder, file_name)
                    self.total_files += 1
                    self.save_file(href, file_path)

    def process_page(self, url):
        if self.is_cancelled():
            return
        soup = self.fetch_page(url)
        if not soup:
            return

        title_element = soup.select_one(self.title_selector)
        folder_name = self.sanitize_folder_name(title_element.text.strip()) if title_element else 'SimpCity_Download'
        download_folder = os.path.join(self.download_folder, folder_name)
        os.makedirs(download_folder, exist_ok=True)

        message_inners = soup.select(self.posts_selector)
        for post in message_inners:
            if self.is_cancelled():
                return
            post_content = post.select_one(self.post_content_selector)
            if post_content:
                self.process_post(post_content, download_folder)

        next_page = soup.select_one(self.next_page_selector)
        if next_page and not self.is_cancelled():
            next_page_url = next_page.get('href')
            if next_page_url:
                self.process_page(self.base_url + next_page_url)

    def download_images_from_simpcity(self, url):
        self.log(self.tr(f"Procesando hilo: {url}"))
        # Set base_url from the initial URL for pagination
        parsed = urlparse(url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.process_page(url)
        self.log(self.tr("Descarga completada."))
