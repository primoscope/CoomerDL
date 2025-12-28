"""
Options Panel Component Module

Handles download type checkboxes (images, videos, compressed files).
Extracted from ui.py to improve modularity.
"""
import customtkinter as ctk
from typing import Callable, Dict


class OptionsPanel(ctk.CTkFrame):
    """
    Options panel component with download type checkboxes.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
    ):
        """
        Initialize the options panel.
        
        Args:
            parent: Parent widget
            tr: Translation function
        """
        super().__init__(parent)
        
        self.tr = tr
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all option panel widgets."""
        # Download images checkbox
        self.download_images_check = ctk.CTkCheckBox(
            self,
            text=self.tr("Descargar Imágenes")
        )
        self.download_images_check.pack(side='left', padx=10)
        self.download_images_check.select()
        
        # Download videos checkbox
        self.download_videos_check = ctk.CTkCheckBox(
            self,
            text=self.tr("Descargar Vídeos")
        )
        self.download_videos_check.pack(side='left', padx=10)
        self.download_videos_check.select()
        
        # Download compressed checkbox
        self.download_compressed_check = ctk.CTkCheckBox(
            self,
            text=self.tr("Descargar Comprimidos")
        )
        self.download_compressed_check.pack(side='left', padx=10)
        self.download_compressed_check.select()
        
        # Download documents checkbox (NEW)
        self.download_documents_check = ctk.CTkCheckBox(
            self,
            text=self.tr("Descargar Documentos")
        )
        self.download_documents_check.pack(side='left', padx=10)
        self.download_documents_check.select()

        # Advanced options frame
        self.advanced_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_frame.pack(side='top', fill='x', pady=(10, 0), padx=10)

        # Dynamic Mode (Headless)
        self.use_dynamic_mode_check = ctk.CTkCheckBox(
            self.advanced_frame,
            text=self.tr("Dynamic Mode (Slow)"),
            command=self._on_dynamic_mode_toggle
        )
        self.use_dynamic_mode_check.pack(side='left', padx=10)

        # Crawl Depth
        self.crawl_depth_label = ctk.CTkLabel(self.advanced_frame, text=self.tr("Crawl Depth: 0"))
        self.crawl_depth_label.pack(side='left', padx=(20, 5))

        self.crawl_depth_slider = ctk.CTkSlider(
            self.advanced_frame,
            from_=0,
            to=5,
            number_of_steps=5,
            width=100,
            command=self._on_depth_change
        )
        self.crawl_depth_slider.pack(side='left', padx=5)
        self.crawl_depth_slider.set(0)

    def _on_depth_change(self, value):
        self.crawl_depth_label.configure(text=self.tr(f"Crawl Depth: {int(value)}"))

    def _on_dynamic_mode_toggle(self):
        # Could show warning about speed
        pass
    
    def get_download_images(self) -> bool:
        """Get the download images checkbox state."""
        return bool(self.download_images_check.get())
    
    def get_download_videos(self) -> bool:
        """Get the download videos checkbox state."""
        return bool(self.download_videos_check.get())
    
    def get_download_compressed(self) -> bool:
        """Get the download compressed checkbox state."""
        return bool(self.download_compressed_check.get())
    
    def get_download_documents(self) -> bool:
        """Get the download documents checkbox state."""
        return bool(self.download_documents_check.get())

    def get_use_dynamic_mode(self) -> bool:
        """Get dynamic mode state."""
        return bool(self.use_dynamic_mode_check.get())

    def get_crawl_depth(self) -> int:
        """Get crawl depth."""
        return int(self.crawl_depth_slider.get())
    
    def get_options(self) -> Dict[str, bool]:
        """Get all download options as a dictionary."""
        return {
            'download_images': self.get_download_images(),
            'download_videos': self.get_download_videos(),
            'download_compressed': self.get_download_compressed(),
            'download_documents': self.get_download_documents(),
            'use_headless_browser': self.get_use_dynamic_mode(),
            'crawl_depth': self.get_crawl_depth(),
        }
    
    def set_options(self, options: Dict[str, bool]):
        """Set download options from a dictionary."""
        if options.get('download_images', True):
            self.download_images_check.select()
        else:
            self.download_images_check.deselect()
        
        if options.get('download_videos', True):
            self.download_videos_check.select()
        else:
            self.download_videos_check.deselect()
        
        if options.get('download_compressed', True):
            self.download_compressed_check.select()
        else:
            self.download_compressed_check.deselect()
        
        if options.get('download_documents', True):
            self.download_documents_check.select()
        else:
            self.download_documents_check.deselect()
    
    def update_texts(self):
        """Update UI texts for translation changes."""
        self.download_images_check.configure(text=self.tr("Descargar Imágenes"))
        self.download_videos_check.configure(text=self.tr("Descargar Vídeos"))
        self.download_compressed_check.configure(text=self.tr("Descargar Comprimidos"))
        self.download_documents_check.configure(text=self.tr("Descargar Documentos"))
