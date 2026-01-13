"""
Gallery Viewer Component
Displays downloaded media with thumbnails and preview functionality
"""
import customtkinter as ctk
from typing import Optional, Callable, List
from pathlib import Path
from PIL import Image, ImageTk
import os


class GalleryViewer(ctk.CTkFrame):
    """
    Gallery viewer for browsing downloaded media files.
    Displays thumbnails in a grid with preview functionality.
    """
    
    SUPPORTED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    SUPPORTED_VIDEO_EXTS = {'.mp4', '.mkv', '.webm', '.mov', '.avi'}
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        download_folder: Optional[str] = None,
    ):
        super().__init__(parent)
        
        self.tr = tr
        self.download_folder = download_folder
        self.current_filter = "all"
        self.media_items = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create gallery widgets."""
        # Search and filter bar
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text=self.tr("Search files..."),
            height=35
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.search_entry.bind("<Return>", lambda e: self.apply_search())
        
        # Search button
        search_btn = ctk.CTkButton(
            control_frame,
            text=self.tr("🔍"),
            width=50,
            command=self.apply_search
        )
        search_btn.pack(side="left", padx=5)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            control_frame,
            text=self.tr("🔄"),
            width=50,
            command=self.refresh_gallery
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        filters = [
            ("All", "all"),
            ("Images", "image"),
            ("Videos", "video"),
            ("Other", "other")
        ]
        
        for label, filter_type in filters:
            btn = ctk.CTkButton(
                filter_frame,
                text=self.tr(label),
                width=80,
                command=lambda f=filter_type: self.set_filter(f)
            )
            btn.pack(side="left", padx=2)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 10),
            text_color="gray"
        )
        self.info_label.pack(anchor="w", padx=15, pady=5)
        
        # Scrollable grid for media items
        self.grid_frame = ctk.CTkScrollableFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)
        self.grid_frame.grid_columnconfigure(3, weight=1)
    
    def set_download_folder(self, folder: str):
        """Set the download folder and refresh gallery."""
        self.download_folder = folder
        self.refresh_gallery()
    
    def set_filter(self, filter_type: str):
        """Set the current filter and refresh display."""
        self.current_filter = filter_type
        self.refresh_gallery()
    
    def apply_search(self):
        """Apply search filter."""
        self.refresh_gallery()
    
    def refresh_gallery(self):
        """Scan folder and display media items."""
        # Clear existing items
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        if not self.download_folder or not os.path.exists(self.download_folder):
            placeholder = ctk.CTkLabel(
                self.grid_frame,
                text=self.tr("No folder selected or folder does not exist."),
                font=("Arial", 12),
                text_color="gray"
            )
            placeholder.grid(row=0, column=0, columnspan=4, pady=50)
            self.info_label.configure(text="")
            return
        
        # Scan for media files
        self.media_items = self.scan_media_files()
        
        # Apply filters
        filtered_items = self.filter_items(self.media_items)
        
        # Update info
        self.info_label.configure(
            text=self.tr(f"Showing {len(filtered_items)} of {len(self.media_items)} files")
        )
        
        if not filtered_items:
            placeholder = ctk.CTkLabel(
                self.grid_frame,
                text=self.tr("No media files found."),
                font=("Arial", 12),
                text_color="gray"
            )
            placeholder.grid(row=0, column=0, columnspan=4, pady=50)
            return
        
        # Display items in grid
        row, col = 0, 0
        for item in filtered_items[:100]:  # Limit to 100 for performance
            self.create_media_card(item, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
    
    def scan_media_files(self) -> List[dict]:
        """Scan download folder for media files."""
        media_items = []
        
        try:
            folder_path = Path(self.download_folder)
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in self.SUPPORTED_IMAGE_EXTS or ext in self.SUPPORTED_VIDEO_EXTS:
                        file_type = "image" if ext in self.SUPPORTED_IMAGE_EXTS else "video"
                        media_items.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'type': file_type,
                            'size': file_path.stat().st_size,
                            'ext': ext
                        })
        except Exception as e:
            print(f"Error scanning folder: {e}")
        
        return media_items
    
    def filter_items(self, items: List[dict]) -> List[dict]:
        """Filter items based on current filter and search."""
        filtered = items
        
        # Apply type filter
        if self.current_filter != "all":
            filtered = [item for item in filtered if item['type'] == self.current_filter]
        
        # Apply search filter
        search_text = self.search_entry.get().strip().lower()
        if search_text:
            filtered = [item for item in filtered if search_text in item['name'].lower()]
        
        return filtered
    
    def create_media_card(self, item: dict, row: int, col: int):
        """Create a card for a media item."""
        card = ctk.CTkFrame(self.grid_frame, width=180, height=220)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        card.grid_propagate(False)
        
        # Thumbnail
        thumbnail_frame = ctk.CTkFrame(card, width=160, height=160, fg_color="gray20")
        thumbnail_frame.pack(padx=10, pady=(10, 5))
        thumbnail_frame.pack_propagate(False)
        
        # Try to load thumbnail
        if item['type'] == 'image':
            try:
                img = Image.open(item['path'])
                img.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(img)
                
                img_label = ctk.CTkLabel(thumbnail_frame, image=photo, text="")
                img_label.image = photo  # Keep reference
                img_label.pack(expand=True)
            except:
                # Fallback icon
                icon_label = ctk.CTkLabel(
                    thumbnail_frame,
                    text="🖼",
                    font=("Arial", 48)
                )
                icon_label.pack(expand=True)
        else:
            # Video icon
            icon_label = ctk.CTkLabel(
                thumbnail_frame,
                text="🎬",
                font=("Arial", 48)
            )
            icon_label.pack(expand=True)
        
        # Filename (truncated)
        name = item['name']
        if len(name) > 20:
            name = name[:17] + "..."
        
        name_label = ctk.CTkLabel(
            card,
            text=name,
            font=("Arial", 10),
            wraplength=160
        )
        name_label.pack(pady=2)
        
        # Size
        size_mb = item['size'] / (1024 * 1024)
        size_label = ctk.CTkLabel(
            card,
            text=f"{size_mb:.1f} MB",
            font=("Arial", 9),
            text_color="gray"
        )
        size_label.pack()
        
        # Make card clickable
        def open_file(event=None):
            import subprocess
            import sys
            if sys.platform == 'win32':
                os.startfile(item['path'])
            elif sys.platform == 'darwin':
                subprocess.call(['open', item['path']])
            else:
                subprocess.call(['xdg-open', item['path']])
        
        card.bind("<Button-1>", open_file)
        for child in card.winfo_children():
            child.bind("<Button-1>", open_file)
