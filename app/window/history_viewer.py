"""
History Viewer Component
Displays searchable download history from database
"""
from __future__ import annotations

import customtkinter as ctk
from typing import Optional, Callable, List
import sqlite3
from datetime import datetime
import os


class HistoryViewer(ctk.CTkFrame):
    """
    History viewer for browsing download history.
    Displays all past downloads with search and filter capabilities.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        db_path: Optional[str] = None,
    ):
        super().__init__(parent)
        
        self.tr = tr
        self.db_path = db_path or "resources/config/downloads.db"
        self.history_items = []
        
        self.create_widgets()
        self.load_history()
    
    def create_widgets(self):
        """Create history viewer widgets."""
        # Search and control bar
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text=self.tr("Search history..."),
            height=35
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.search_entry.bind("<Return>", lambda e: self.apply_search())
        
        # Search button
        search_btn = ctk.CTkButton(
            control_frame,
            text=self.tr("🔍 Search"),
            width=100,
            command=self.apply_search
        )
        search_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ctk.CTkButton(
            control_frame,
            text=self.tr("📤 Export"),
            width=100,
            command=self.export_history
        )
        export_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            control_frame,
            text=self.tr("🗑 Clear"),
            width=100,
            command=self.clear_history,
            fg_color="darkred",
            hover_color="red"
        )
        clear_btn.pack(side="left", padx=(5, 10))
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=("Arial", 11),
            text_color="gray"
        )
        self.stats_label.pack(anchor="w", padx=5)
        
        # History list (scrollable)
        self.history_scroll = ctk.CTkScrollableFrame(
            self,
            label_text=self.tr("Download History")
        )
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_history(self):
        """Load history from database."""
        self.history_items = []
        
        if not os.path.exists(self.db_path):
            self.update_display()
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query all downloads ordered by date
            cursor.execute("""
                SELECT media_url, file_path, file_size, user_id, post_id, downloaded_at
                FROM downloads
                ORDER BY downloaded_at DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                url, file_path, file_size, user_id, post_id, downloaded_at = row
                
                # Determine status (file still exists?)
                status = "completed" if file_path and os.path.exists(file_path) else "deleted"
                
                self.history_items.append({
                    'url': url,
                    'file_path': file_path,
                    'file_size': file_size or 0,
                    'user_id': user_id,
                    'post_id': post_id,
                    'date': downloaded_at,
                    'status': status
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading history: {e}")
        
        self.update_display()
    
    def apply_search(self):
        """Apply search filter."""
        self.update_display()
    
    def update_display(self):
        """Update the history display."""
        # Clear existing items
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
        
        # Filter items based on search
        filtered_items = self.filter_items(self.history_items)
        
        # Update stats
        total_count = len(self.history_items)
        total_size = sum(item['file_size'] for item in self.history_items) / (1024 * 1024 * 1024)  # GB
        filtered_count = len(filtered_items)
        
        self.stats_label.configure(
            text=self.tr(
                f"Total: {total_count} downloads | Size: {total_size:.2f} GB | "
                f"Showing: {filtered_count} items"
            )
        )
        
        if not filtered_items:
            placeholder = ctk.CTkLabel(
                self.history_scroll,
                text=self.tr("No history found."),
                font=("Arial", 12),
                text_color="gray"
            )
            placeholder.pack(pady=50)
            return
        
        # Display items
        for item in filtered_items[:500]:  # Limit to 500 for performance
            self.create_history_item(item)
    
    def filter_items(self, items: List[dict]) -> List[dict]:
        """Filter items based on search text."""
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            return items
        
        return [
            item for item in items
            if search_text in item['url'].lower()
            or (item['user_id'] and search_text in item['user_id'].lower())
            or (item['post_id'] and search_text in item['post_id'].lower())
        ]
    
    def create_history_item(self, item: dict):
        """Create a history item widget."""
        item_frame = ctk.CTkFrame(self.history_scroll)
        item_frame.pack(fill="x", pady=2, padx=5)
        
        # Status indicator
        status_colors = {
            "completed": "green",
            "deleted": "red"
        }
        color = status_colors.get(item['status'], "gray")
        
        status_label = ctk.CTkLabel(
            item_frame,
            text="●",
            text_color=color,
            font=("Arial", 16)
        )
        status_label.pack(side="left", padx=5)
        
        # Info frame
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # URL
        url_text = item['url']
        if len(url_text) > 100:
            url_text = url_text[:97] + "..."
        
        url_label = ctk.CTkLabel(
            info_frame,
            text=url_text,
            anchor="w",
            font=("Arial", 11)
        )
        url_label.pack(anchor="w")
        
        # Details
        size_mb = item['file_size'] / (1024 * 1024)
        date_str = item['date']
        try:
            date_obj = datetime.fromisoformat(date_str)
            date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            date_formatted = date_str[:16] if date_str else "Unknown"
        
        details_text = f"{item['status'].title()} | {size_mb:.1f} MB | {date_formatted}"
        if item['user_id']:
            details_text += f" | User: {item['user_id']}"
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            anchor="w",
            font=("Arial", 9),
            text_color="gray"
        )
        details_label.pack(anchor="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=5)
        
        if item['status'] == 'completed' and item['file_path']:
            open_btn = ctk.CTkButton(
                action_frame,
                text=self.tr("📂 Open"),
                width=80,
                height=25,
                command=lambda: self.open_file(item['file_path'])
            )
            open_btn.pack(side="left", padx=2)
    
    def open_file(self, file_path: str):
        """Open file in system viewer."""
        import subprocess
        import sys
        
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def export_history(self):
        """Export history to CSV file."""
        from tkinter import filedialog
        import csv
        
        if not self.history_items:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=self.tr("Export History")
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'File Path', 'Size (MB)', 'User ID', 'Post ID', 'Date', 'Status'])
                
                for item in self.history_items:
                    size_mb = item['file_size'] / (1024 * 1024)
                    writer.writerow([
                        item['url'],
                        item['file_path'],
                        f"{size_mb:.2f}",
                        item['user_id'],
                        item['post_id'],
                        item['date'],
                        item['status']
                    ])
            
            print(f"History exported to {file_path}")
        except Exception as e:
            print(f"Error exporting history: {e}")
    
    def clear_history(self):
        """Clear all history (with confirmation)."""
        from tkinter import messagebox
        
        if not self.history_items:
            return
        
        confirm = messagebox.askyesno(
            self.tr("Confirm Clear"),
            self.tr("Are you sure you want to clear all download history?\nThis cannot be undone."),
            icon='warning'
        )
        
        if not confirm:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM downloads")
            conn.commit()
            conn.close()
            
            self.history_items = []
            self.update_display()
            
            print("History cleared")
        except Exception as e:
            print(f"Error clearing history: {e}")
    
    def refresh(self):
        """Refresh history from database."""
        self.load_history()
