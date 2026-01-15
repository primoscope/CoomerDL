from __future__ import annotations

import os
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from downloader.base import BaseDownloader, DownloadResult, DownloadOptions
from downloader.factory import DownloaderFactory

@DownloaderFactory.register
class Jpg5Downloader(BaseDownloader):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "jpg5.su" in url

    def supports_url(self, url: str) -> bool:
        return "jpg5.su" in url

    def get_site_name(self) -> str:
        return "Jpg5"

    def download(self, url: str) -> DownloadResult:
        self.reset()
        start_time = time.time()
        self.log(self.tr(f"Iniciando descarga desde: {url}"))

        try:
            if not os.path.exists(self.download_folder):
                os.makedirs(self.download_folder)

            response = self.safe_request(url)
            if not response:
                return DownloadResult(False, 0, 0, error_message="Failed to fetch page")

            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='list-item c8 gutter-margin-right-bottom')
            self.total_files = len(divs)
            self.log(self.tr(f"Total de elementos a procesar: {self.total_files}"))

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for i, div in enumerate(divs):
                    if self.is_cancelled():
                        break

                    enlaces = div.find_all('a', class_='image-container --media')
                    for enlace in enlaces:
                        if self.is_cancelled():
                            break
                        futures.append(executor.submit(self._process_link, enlace))

                for future in futures:
                    if self.is_cancelled():
                        break
                    future.result()

            return DownloadResult(
                success=self.completed_files > 0,
                total_files=self.total_files,
                completed_files=self.completed_files,
                failed_files=self.failed_files,
                elapsed_seconds=time.time() - start_time
            )

        except Exception as e:
            self.log(self.tr(f"Error general: {e}"))
            return DownloadResult(False, 0, 0, error_message=str(e))

    def _process_link(self, enlace):
        if self.is_cancelled():
            return

        try:
            media_url = enlace['href']
            self.log(self.tr(f"Procesando enlace: {media_url}"))

            media_response = self.safe_request(media_url)
            if not media_response:
                return

            media_soup = BeautifulSoup(media_response.content, 'html.parser')
            header_content = media_soup.find('div', class_='header-content-right')

            if header_content:
                btn_descarga = header_content.find('a', class_='btn btn-download default')
                if btn_descarga and 'href' in btn_descarga.attrs:
                    descarga_url = btn_descarga['href']
                    self.log(self.tr(f"Descargando desde: {descarga_url}"))

                    filename = os.path.basename(descarga_url)
                    filepath = os.path.join(self.download_folder, filename)

                    if self.download_file(descarga_url, filepath):
                        self.completed_files += 1
                        self.report_global_progress()
                        self.log(self.tr(f"Imagen descargada: {filename}"))
                    else:
                        self.failed_files.append(descarga_url)
                else:
                    self.log(self.tr("No se encontró el enlace de descarga."))
            else:
                self.log(self.tr("No se encontró la clase 'header-content-right'."))

        except Exception as e:
            self.log(self.tr(f"Error al procesar el enlace: {e}"))
            self.failed_files.append(enlace.get('href', 'unknown'))
