"""
Input Panel Component Module

Handles URL entry and folder selection for downloads.
Extracted from ui.py to improve modularity.
"""
import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional


class InputPanel(ctk.CTkFrame):
    """
    Input panel component with URL entry and folder selection.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        on_folder_change: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the input panel.
        
        Args:
            parent: Parent widget
            tr: Translation function
            on_folder_change: Callback when folder is selected
        """
        super().__init__(parent)
        
        self.tr = tr
        self.on_folder_change = on_folder_change
        self.download_folder = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all input panel widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # URL label
        self.url_label = ctk.CTkLabel(self, text=self.tr("URL de la página web:"))
        self.url_label.grid(row=0, column=0, sticky='w')
        
        # URL entry
        self.url_entry = ctk.CTkEntry(self)
        self.url_entry.grid(row=1, column=0, sticky='ew', padx=(0, 5))
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            self,
            text=self.tr("Seleccionar Carpeta"),
            command=self.select_folder
        )
        self.browse_button.grid(row=1, column=1, sticky='e')
        
        # Folder path label
        self.folder_path = ctk.CTkLabel(
            self,
            text="",
            cursor="hand2",
            font=("Arial", 13)
        )
        self.folder_path.grid(row=2, column=0, columnspan=2, sticky='w')
        self.folder_path.bind("<Button-1>", self.open_download_folder)
        self.folder_path.bind("<Enter>", self.on_hover_enter)
        self.folder_path.bind("<Leave>", self.on_hover_leave)
    
    def select_folder(self):
        """Open folder selection dialog."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_path.configure(text=folder_selected)
            if self.on_folder_change:
                self.on_folder_change(folder_selected)
    
    def open_download_folder(self, event=None):
        """Open the selected download folder in file explorer."""
        if self.download_folder and os.path.exists(self.download_folder):
            if sys.platform == "win32":
                os.startfile(self.download_folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.download_folder])
            else:
                subprocess.Popen(["xdg-open", self.download_folder])
        else:
            messagebox.showerror(
                self.tr("Error"),
                self.tr("La carpeta no existe o no es válida.")
            )
    
    def on_hover_enter(self, event):
        """Add underline on hover."""
        self.folder_path.configure(font=("Arial", 13, "underline"))
    
    def on_hover_leave(self, event):
        """Remove underline on hover exit."""
        self.folder_path.configure(font=("Arial", 13))
    
    def get_url(self) -> str:
        """Get the entered URL."""
        return self.url_entry.get().strip()
    
    def get_download_folder(self) -> str:
        """Get the selected download folder."""
        return self.download_folder
    
    def set_download_folder(self, path: str):
        """Set the download folder and update display."""
        self.download_folder = path
        self.folder_path.configure(text=path)
    
    def get_url_entry_widget(self):
        """Get the URL entry widget for context menu binding."""
        return self.url_entry
    
    def update_texts(self):
        """Update UI texts for translation changes."""
        self.url_label.configure(text=self.tr("URL de la página web:"))
        self.browse_button.configure(text=self.tr("Seleccionar Carpeta"))
