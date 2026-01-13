"""
Command Center Dashboard - Tabbed Interface
Main window with tabs for Home, Queue, Gallery, and History
"""
import customtkinter as ctk
from typing import Optional, Callable
from pathlib import Path


class CommandCenterDashboard(ctk.CTkFrame):
    """
    Main dashboard with tabbed interface for different app functions.
    
    Tabs:
    - Home: URL input and quick stats
    - Queue: Active downloads with controls
    - Gallery: Media viewer for downloaded files
    - History: Searchable download history
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        on_download: Optional[Callable[[str, str], None]] = None,
        on_folder_select: Optional[Callable] = None,
    ):
        super().__init__(parent)
        
        self.tr = tr
        self.on_download = on_download
        self.on_folder_select = on_folder_select
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self, width=800, height=600)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_home = self.tabview.add(self.tr("Home"))
        self.tab_queue = self.tabview.add(self.tr("Queue"))
        self.tab_gallery = self.tabview.add(self.tr("Gallery"))
        self.tab_history = self.tabview.add(self.tr("History"))
        
        # Initialize tabs
        self.create_home_tab()
        self.create_queue_tab()
        self.create_gallery_tab()
        self.create_history_tab()
    
    def create_home_tab(self):
        """Create the Home tab with URL input and quick stats."""
        # Main container
        home_container = ctk.CTkFrame(self.tab_home)
        home_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            home_container,
            text=self.tr("Welcome to CoomerDL"),
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(home_container)
        url_frame.pack(fill="x", padx=10, pady=10)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text=self.tr("Enter URL(s):"),
            font=("Arial", 14, "bold")
        )
        url_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Multi-line URL textbox for batch input
        self.url_textbox = ctk.CTkTextbox(
            url_frame,
            height=100,
            wrap="none"
        )
        self.url_textbox.pack(fill="x", padx=10, pady=5)
        self.url_textbox.insert("1.0", self.tr("Enter one URL per line..."))
        
        # Folder selection
        folder_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=10, pady=5)
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text=self.tr("Download Folder:"),
            font=("Arial", 12)
        )
        folder_label.pack(side="left", padx=(0, 10))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text=self.tr("Select folder..."),
            width=400
        )
        self.folder_entry.pack(side="left", fill="x", expand=True)
        
        browse_button = ctk.CTkButton(
            folder_frame,
            text=self.tr("Browse"),
            command=self.on_folder_select,
            width=100
        )
        browse_button.pack(side="left", padx=(10, 0))
        
        # Download button
        download_button = ctk.CTkButton(
            url_frame,
            text=self.tr("⬇ Download"),
            command=self.start_download,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        download_button.pack(pady=(10, 10))
        
        # Quick Stats Section
        stats_frame = ctk.CTkFrame(home_container)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text=self.tr("Quick Stats"),
            font=("Arial", 16, "bold")
        )
        stats_title.pack(pady=(10, 10))
        
        # Stats grid
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="both", expand=True, padx=20)
        
        # Row 1
        row1 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.stat_total = self.create_stat_card(row1, self.tr("Total Downloads"), "0")
        self.stat_total.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stat_active = self.create_stat_card(row1, self.tr("Active"), "0")
        self.stat_active.pack(side="left", fill="x", expand=True, padx=5)
        
        # Row 2
        row2 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.stat_completed = self.create_stat_card(row2, self.tr("Completed"), "0")
        self.stat_completed.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stat_failed = self.create_stat_card(row2, self.tr("Failed"), "0")
        self.stat_failed.pack(side="left", fill="x", expand=True, padx=5)
    
    def create_stat_card(self, parent, label: str, value: str) -> ctk.CTkFrame:
        """Create a stat card widget."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        
        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=("Arial", 12),
            text_color="gray"
        )
        label_widget.pack(pady=(10, 5))
        
        value_widget = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 24, "bold")
        )
        value_widget.pack(pady=(5, 10))
        
        # Store reference to value label for updates
        card.value_label = value_widget
        
        return card
    
    def create_queue_tab(self):
        """Create the Queue tab with active downloads."""
        queue_label = ctk.CTkLabel(
            self.tab_queue,
            text=self.tr("Queue Manager"),
            font=("Arial", 20, "bold")
        )
        queue_label.pack(pady=20)
        
        # Placeholder for queue integration
        info_label = ctk.CTkLabel(
            self.tab_queue,
            text=self.tr("Queue manager will be integrated here.\nUse the Queue button in the menu for now."),
            font=("Arial", 12),
            text_color="gray"
        )
        info_label.pack(pady=20)
        
        # This will be replaced with actual QueueDialog content
        # when integrated with app/dialogs/queue_dialog.py
    
    def create_gallery_tab(self):
        """Create the Gallery tab with media viewer."""
        gallery_label = ctk.CTkLabel(
            self.tab_gallery,
            text=self.tr("Media Gallery"),
            font=("Arial", 20, "bold")
        )
        gallery_label.pack(pady=20)
        
        # Search bar
        search_frame = ctk.CTkFrame(self.tab_gallery)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.tr("Search downloaded media..."),
            height=35
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        search_button = ctk.CTkButton(
            search_frame,
            text=self.tr("🔍 Search"),
            width=100
        )
        search_button.pack(side="left", padx=(5, 10))
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(self.tab_gallery, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(filter_frame, text=self.tr("All"), width=80).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text=self.tr("Images"), width=80).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text=self.tr("Videos"), width=80).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text=self.tr("Other"), width=80).pack(side="left", padx=2)
        
        # Scrollable gallery grid
        self.gallery_scroll = ctk.CTkScrollableFrame(
            self.tab_gallery,
            label_text=self.tr("Downloaded Media")
        )
        self.gallery_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Placeholder message
        placeholder = ctk.CTkLabel(
            self.gallery_scroll,
            text=self.tr("No media downloaded yet.\nYour downloaded files will appear here."),
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(pady=50)
    
    def create_history_tab(self):
        """Create the History tab with searchable download log."""
        history_label = ctk.CTkLabel(
            self.tab_history,
            text=self.tr("Download History"),
            font=("Arial", 20, "bold")
        )
        history_label.pack(pady=20)
        
        # Search and filter bar
        search_frame = ctk.CTkFrame(self.tab_history)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.tr("Search history..."),
            height=35
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        search_button = ctk.CTkButton(
            search_frame,
            text=self.tr("🔍 Search"),
            width=100
        )
        search_button.pack(side="left", padx=5)
        
        export_button = ctk.CTkButton(
            search_frame,
            text=self.tr("📤 Export"),
            width=100
        )
        export_button.pack(side="left", padx=(5, 10))
        
        # Stats summary
        stats_frame = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        stats_text = ctk.CTkLabel(
            stats_frame,
            text=self.tr("Total Downloads: 0 | Total Size: 0 MB | Success Rate: 0%"),
            font=("Arial", 11),
            text_color="gray"
        )
        stats_text.pack(anchor="w")
        
        # History list (scrollable)
        self.history_scroll = ctk.CTkScrollableFrame(
            self.tab_history,
            label_text=self.tr("Recent Downloads")
        )
        self.history_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Placeholder message
        placeholder = ctk.CTkLabel(
            self.history_scroll,
            text=self.tr("No download history yet.\nYour download history will appear here."),
            font=("Arial", 12),
            text_color="gray"
        )
        placeholder.pack(pady=50)
    
    def start_download(self):
        """Handle download button click."""
        urls_text = self.url_textbox.get("1.0", "end-1c").strip()
        folder = self.folder_entry.get().strip()
        
        if not urls_text or urls_text == self.tr("Enter one URL per line..."):
            return
        
        if not folder:
            return
        
        # Parse URLs (one per line)
        urls = [line.strip() for line in urls_text.split('\n') if line.strip()]
        
        if self.on_download and urls:
            for url in urls:
                self.on_download(url, folder)
    
    def update_stats(self, total: int = 0, active: int = 0, completed: int = 0, failed: int = 0):
        """Update the quick stats display."""
        self.stat_total.value_label.configure(text=str(total))
        self.stat_active.value_label.configure(text=str(active))
        self.stat_completed.value_label.configure(text=str(completed))
        self.stat_failed.value_label.configure(text=str(failed))
    
    def get_urls(self) -> list:
        """Get list of URLs from textbox."""
        urls_text = self.url_textbox.get("1.0", "end-1c").strip()
        if urls_text and urls_text != self.tr("Enter one URL per line..."):
            return [line.strip() for line in urls_text.split('\n') if line.strip()]
        return []
    
    def get_download_folder(self) -> str:
        """Get selected download folder."""
        return self.folder_entry.get().strip()
    
    def set_download_folder(self, folder: str):
        """Set the download folder."""
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, folder)
    
    def add_history_item(self, url: str, status: str, size: str, date: str):
        """Add an item to the history list."""
        item_frame = ctk.CTkFrame(self.history_scroll)
        item_frame.pack(fill="x", pady=2, padx=5)
        
        # Status indicator
        status_colors = {
            "completed": "green",
            "failed": "red",
            "cancelled": "orange"
        }
        color = status_colors.get(status.lower(), "gray")
        
        status_label = ctk.CTkLabel(
            item_frame,
            text="●",
            text_color=color,
            font=("Arial", 16)
        )
        status_label.pack(side="left", padx=5)
        
        # URL and info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        url_label = ctk.CTkLabel(
            info_frame,
            text=url[:80] + "..." if len(url) > 80 else url,
            anchor="w",
            font=("Arial", 11)
        )
        url_label.pack(anchor="w")
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=f"{status.title()} | {size} | {date}",
            anchor="w",
            font=("Arial", 9),
            text_color="gray"
        )
        details_label.pack(anchor="w")
