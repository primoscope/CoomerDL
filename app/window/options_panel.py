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
    
    def get_download_images(self) -> bool:
        """Get the download images checkbox state."""
        return bool(self.download_images_check.get())
    
    def get_download_videos(self) -> bool:
        """Get the download videos checkbox state."""
        return bool(self.download_videos_check.get())
    
    def get_download_compressed(self) -> bool:
        """Get the download compressed checkbox state."""
        return bool(self.download_compressed_check.get())
    
    def get_options(self) -> Dict[str, bool]:
        """Get all download options as a dictionary."""
        return {
            'download_images': self.get_download_images(),
            'download_videos': self.get_download_videos(),
            'download_compressed': self.get_download_compressed(),
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
    
    def update_texts(self):
        """Update UI texts for translation changes."""
        self.download_images_check.configure(text=self.tr("Descargar Imágenes"))
        self.download_videos_check.configure(text=self.tr("Descargar Vídeos"))
        self.download_compressed_check.configure(text=self.tr("Descargar Comprimidos"))
