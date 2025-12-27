"""
Action Panel Component Module

Handles download and cancel buttons with progress label.
Extracted from ui.py to improve modularity.
"""
import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional


class ActionPanel(ctk.CTkFrame):
    """
    Action panel component with download/cancel buttons and progress label.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        on_download: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        autoscroll_var: Optional[tk.BooleanVar] = None,
    ):
        """
        Initialize the action panel.
        
        Args:
            parent: Parent widget
            tr: Translation function
            on_download: Callback for download button
            on_cancel: Callback for cancel button
            autoscroll_var: Variable for autoscroll checkbox
        """
        super().__init__(parent)
        
        self.tr = tr
        self.on_download = on_download
        self.on_cancel = on_cancel
        self.autoscroll_var = autoscroll_var
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all action panel widgets."""
        # Download button
        self.download_button = ctk.CTkButton(
            self,
            text=self.tr("Descargar"),
            command=self.on_download
        )
        self.download_button.pack(side='left', padx=10)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self,
            text=self.tr("Cancelar Descarga"),
            state="disabled",
            command=self.on_cancel
        )
        self.cancel_button.pack(side='left', padx=10)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(self, text="")
        self.progress_label.pack(side='left', padx=10)
        
        # Autoscroll checkbox (if provided)
        if self.autoscroll_var is not None:
            self.autoscroll_logs_checkbox = ctk.CTkCheckBox(
                self,
                text=self.tr("Auto-scroll logs"),
                variable=self.autoscroll_var
            )
            self.autoscroll_logs_checkbox.pack(side="right")
    
    def set_download_button_state(self, state: str):
        """Set the download button state ('normal' or 'disabled')."""
        self.download_button.configure(state=state)
    
    def set_cancel_button_state(self, state: str):
        """Set the cancel button state ('normal' or 'disabled')."""
        self.cancel_button.configure(state=state)
    
    def set_progress_label_text(self, text: str):
        """Set the progress label text."""
        self.progress_label.configure(text=text)
    
    def enable_download(self):
        """Enable download button and disable cancel button."""
        self.download_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
    
    def enable_cancel(self):
        """Disable download button and enable cancel button."""
        self.download_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
    
    def update_texts(self):
        """Update UI texts for translation changes."""
        self.download_button.configure(text=self.tr("Descargar"))
        self.cancel_button.configure(text=self.tr("Cancelar Descarga"))
        if hasattr(self, 'autoscroll_logs_checkbox'):
            self.autoscroll_logs_checkbox.configure(text=self.tr("Auto-scroll logs"))
