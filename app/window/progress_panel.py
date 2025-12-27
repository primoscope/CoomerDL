"""
Progress Panel Component Module

Handles progress bar, percentage display, and details toggle.
Extracted from ui.py to improve modularity.
"""
import customtkinter as ctk
from PIL import Image
from typing import Callable, Optional


class ProgressPanel(ctk.CTkFrame):
    """
    Progress panel component with progress bar and percentage display.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        on_toggle_details: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the progress panel.
        
        Args:
            parent: Parent widget
            tr: Translation function
            on_toggle_details: Callback for toggle details button
        """
        super().__init__(parent)
        
        self.tr = tr
        self.on_toggle_details = on_toggle_details
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all progress panel widgets."""
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.progress_bar.set(0)
        
        # Progress percentage label
        self.progress_percentage = ctk.CTkLabel(self, text="0%")
        self.progress_percentage.pack(side='left')
        
        # Toggle details button (icon)
        if self.on_toggle_details:
            self.download_icon = self.load_download_icon()
            if self.download_icon:
                self.toggle_details_button = ctk.CTkLabel(
                    self,
                    image=self.download_icon,
                    text="",
                    cursor="hand2"
                )
                self.toggle_details_button.pack(side='left', padx=(5, 0))
                self.toggle_details_button.bind(
                    "<Button-1>",
                    lambda e: self.on_toggle_details()
                )
                
                # Hover effects
                self.toggle_details_button.bind(
                    "<Enter>",
                    lambda e: self.toggle_details_button.configure(fg_color="gray25")
                )
                self.toggle_details_button.bind(
                    "<Leave>",
                    lambda e: self.toggle_details_button.configure(fg_color="transparent")
                )
    
    def load_download_icon(self):
        """Load and resize the download icon."""
        try:
            img = Image.open('resources/img/iconos/ui/download_icon.png')
            return ctk.CTkImage(img, size=(24, 24))
        except Exception:
            return None
    
    def set_progress(self, value: float):
        """
        Set the progress bar value.
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        self.progress_bar.set(value)
    
    def set_percentage(self, percentage: int):
        """
        Set the percentage text.
        
        Args:
            percentage: Percentage value (0-100)
        """
        self.progress_percentage.configure(text=f"{percentage}%")
    
    def update_progress(self, completed: int, total: int):
        """
        Update progress bar and percentage based on completed/total.
        
        Args:
            completed: Number of completed items
            total: Total number of items
        """
        if total > 0:
            progress = completed / total
            percentage = int(progress * 100)
            self.set_progress(progress)
            self.set_percentage(percentage)
        else:
            self.set_progress(0)
            self.set_percentage(0)
    
    def reset(self):
        """Reset progress to 0."""
        self.set_progress(0)
        self.set_percentage(0)
