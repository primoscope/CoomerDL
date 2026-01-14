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
from urllib.parse import urlparse

try:
    from tkinterdnd2 import DND_FILES
    dnd_available = True
except ImportError:
    dnd_available = False


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

        self.url_count_label = ctk.CTkLabel(self, text="")
        self.url_count_label.grid(row=0, column=1, sticky='e')
        
        # URL entry (multi-line for batch URL support)
        self.url_entry = ctk.CTkTextbox(
            self,
            height=80,
            wrap="none"
        )
        self.url_entry.grid(row=1, column=0, sticky='ew', padx=(0, 5))

        try:
            self.url_entry._textbox.bind('<KeyRelease>', self._on_urls_changed)
        except Exception:
            pass
        
        # Enable Drag & Drop if available
        if dnd_available:
            try:
                # We need to register the underlying tkinter widget
                self.url_entry._textbox.drop_target_register(DND_FILES)
                self.url_entry._textbox.dnd_bind('<<Drop>>', self.on_drop)
            except Exception as e:
                print(f"Warning: Failed to register DnD for textbox: {e}")
        
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

        self.update_url_count()

    def _on_urls_changed(self, event=None):
        self.update_url_count()

    def parse_urls(self, raw_text: str) -> tuple[list[str], list[str]]:
        raw_text = (raw_text or "").strip()
        if not raw_text:
            return [], []

        valid: list[str] = []
        invalid: list[str] = []
        seen = set()

        for line in raw_text.splitlines():
            u = line.strip()
            if not u:
                continue
            if u in seen:
                continue
            seen.add(u)

            try:
                parsed = urlparse(u)
                if parsed.scheme in ("http", "https") and bool(parsed.netloc):
                    valid.append(u)
                else:
                    invalid.append(u)
            except Exception:
                invalid.append(u)

        return valid, invalid

    def update_url_count(self):
        try:
            raw_text = self.url_entry.get("1.0", "end-1c")
        except Exception:
            raw_text = ""

        valid, invalid = self.parse_urls(raw_text)
        if not raw_text.strip():
            self.url_count_label.configure(text="")
            return

        if invalid:
            self.url_count_label.configure(text=self.tr("{valid} valid, {invalid} invalid", valid=len(valid), invalid=len(invalid)))
        else:
            self.url_count_label.configure(text=self.tr("{count} URL(s)", count=len(valid)))
    
    def on_drop(self, event):
        file_list = (event.data or "").strip()
        if not file_list:
            return

        paths: list[str] = []
        buf = ""
        in_braces = False
        for ch in file_list:
            if ch == '{':
                in_braces = True
                buf = ""
                continue
            if ch == '}' and in_braces:
                in_braces = False
                if buf:
                    paths.append(buf)
                buf = ""
                continue
            if ch.isspace() and not in_braces:
                if buf:
                    paths.append(buf)
                    buf = ""
                continue
            buf += ch
        if buf:
            paths.append(buf)

        appended_any = False
        for path in paths:
            if not path:
                continue
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        continue

                    current = self.url_entry.get("1.0", "end-1c").strip()
                    if current:
                        self.url_entry.insert("end", "\n" + content + "\n")
                    else:
                        self.url_entry.insert("end", content + "\n")
                    appended_any = True
                except Exception as e:
                    messagebox.showerror(
                        self.tr("Error"),
                        self.tr("Error reading file: {error}", error=e)
                    )

        if appended_any:
            self.update_url_count()

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
        """Get the entered URL(s). Returns newline-separated URLs for batch processing."""
        return self.url_entry.get("1.0", "end-1c").strip()
    
    def get_urls(self) -> list:
        """Get all entered URLs as a list, filtering out empty lines."""
        raw_text = self.url_entry.get("1.0", "end-1c")
        valid, _invalid = self.parse_urls(raw_text)
        return valid
    
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
        self.update_url_count()
