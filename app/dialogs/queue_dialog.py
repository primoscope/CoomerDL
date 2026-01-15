"""
Download Queue Manager Dialog
"""
from __future__ import annotations

import customtkinter as ctk
from typing import Optional, Callable
from app.models.download_queue import DownloadQueue, QueueItem, QueueItemStatus


class QueueDialog(ctk.CTkToplevel):
    """Dialog window for managing download queue."""
    
    def __init__(
        self,
        parent,
        queue: DownloadQueue,
        tr: Optional[Callable[[str], str]] = None,
        on_process_queue: Optional[Callable[[], None]] = None,
        on_process_all: Optional[Callable[[], None]] = None,
        on_pause_all: Optional[Callable[[], None]] = None,
        on_resume_all: Optional[Callable[[], None]] = None,
        on_stop_processing: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.queue = queue
        self.tr = tr or (lambda x: x)
        self.on_process_queue = on_process_queue
        self.on_process_all = on_process_all
        self.on_pause_all = on_pause_all
        self.on_resume_all = on_resume_all
        self.on_stop_processing = on_stop_processing
        self.selected_item_id = None
        
        # Setup window
        self.title(self.tr("Download Queue"))
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Create UI
        self.create_widgets()
        
        # Bind queue changes to refresh
        self.queue._on_change = self.refresh_queue
        
        # Initial load
        self.refresh_queue()
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Stats frame at top
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=("Arial", 12)
        )
        self.stats_label.pack(pady=5)
        
        # Queue list frame (scrollable)
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create scrollable frame for queue items
        self.scrollable_frame = ctk.CTkScrollableFrame(
            list_frame,
            label_text=self.tr("Queue Items")
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Controls frame at bottom
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(controls_frame, fg_color="transparent")
        left_buttons.pack(side="left", fill="x", expand=True)

        if self.on_pause_all:
            self.btn_pause_all = ctk.CTkButton(
                left_buttons,
                text="⏸⏸ " + self.tr("Pause All"),
                command=self.on_pause_all,
                width=120
            )
            self.btn_pause_all.pack(side="left", padx=2)

        if self.on_resume_all:
            self.btn_resume_all = ctk.CTkButton(
                left_buttons,
                text="▶▶ " + self.tr("Resume All"),
                command=self.on_resume_all,
                width=120
            )
            self.btn_resume_all.pack(side="left", padx=2)
        
        self.btn_move_up = ctk.CTkButton(
            left_buttons,
            text="↑ " + self.tr("Move Up"),
            command=self.move_up,
            width=100
        )
        self.btn_move_up.pack(side="left", padx=2)
        
        self.btn_move_down = ctk.CTkButton(
            left_buttons,
            text="↓ " + self.tr("Move Down"),
            command=self.move_down,
            width=100
        )
        self.btn_move_down.pack(side="left", padx=2)
        
        self.btn_pause = ctk.CTkButton(
            left_buttons,
            text="⏸ " + self.tr("Pause"),
            command=self.pause_selected,
            width=100
        )
        self.btn_pause.pack(side="left", padx=2)
        
        self.btn_resume = ctk.CTkButton(
            left_buttons,
            text="▶ " + self.tr("Resume"),
            command=self.resume_selected,
            width=100
        )
        self.btn_resume.pack(side="left", padx=2)
        
        self.btn_cancel = ctk.CTkButton(
            left_buttons,
            text="✕ " + self.tr("Cancel"),
            command=self.cancel_selected,
            width=100,
            fg_color="darkred"
        )
        self.btn_cancel.pack(side="left", padx=2)
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(controls_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        # Process Queue button (if callback provided)
        if self.on_process_queue:
            self.btn_process = ctk.CTkButton(
                right_buttons,
                text="▶ " + self.tr("Process Queue"),
                command=self.on_process_queue,
                width=130,
                fg_color="green"
            )
            self.btn_process.pack(side="left", padx=2)

        if self.on_process_all:
            self.btn_process_all = ctk.CTkButton(
                right_buttons,
                text="▶▶ " + self.tr("Process All"),
                command=self.on_process_all,
                width=130,
                fg_color="green"
            )
            self.btn_process_all.pack(side="left", padx=2)

        if self.on_stop_processing:
            self.btn_stop_processing = ctk.CTkButton(
                right_buttons,
                text="⏹ " + self.tr("Stop"),
                command=self.on_stop_processing,
                width=90,
                fg_color="darkred"
            )
            self.btn_stop_processing.pack(side="left", padx=2)
        
        self.btn_clear = ctk.CTkButton(
            right_buttons,
            text=self.tr("Clear Completed"),
            command=self.clear_completed,
            width=120
        )
        self.btn_clear.pack(side="left", padx=2)
        
        self.btn_close = ctk.CTkButton(
            right_buttons,
            text=self.tr("Close"),
            command=self.destroy,
            width=100
        )
        self.btn_close.pack(side="left", padx=2)
    
    def create_queue_item_widget(self, item: QueueItem) -> ctk.CTkFrame:
        """Create a widget for a single queue item."""
        # Main item frame
        item_frame = ctk.CTkFrame(self.scrollable_frame)
        
        # Determine colors based on status
        status_colors = {
            QueueItemStatus.PENDING: "gray",
            QueueItemStatus.DOWNLOADING: "blue",
            QueueItemStatus.PAUSED: "orange",
            QueueItemStatus.COMPLETED: "green",
            QueueItemStatus.FAILED: "red",
            QueueItemStatus.CANCELLED: "darkred",
        }
        border_color = status_colors.get(item.status, "gray")
        item_frame.configure(border_width=2, border_color=border_color)
        
        # Make item clickable
        def select_item(event=None):
            self.selected_item_id = item.id
            self.refresh_queue()
        
        item_frame.bind("<Button-1>", select_item)
        
        # Highlight if selected
        if self.selected_item_id == item.id:
            item_frame.configure(fg_color="#2b2b2b")
        
        # Content frame
        content = ctk.CTkFrame(item_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # URL label (truncated)
        url_text = item.url if len(item.url) <= 60 else item.url[:57] + "..."
        url_label = ctk.CTkLabel(
            content,
            text=url_text,
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        url_label.pack(anchor="w")
        url_label.bind("<Button-1>", select_item)
        
        # Status and progress
        status_text = f"Status: {item.status.value.title()}"
        if item.status == QueueItemStatus.DOWNLOADING and item.progress > 0:
            status_text += f" ({item.progress*100:.1f}%)"
        
        status_label = ctk.CTkLabel(
            content,
            text=status_text,
            font=("Arial", 10),
            anchor="w"
        )
        status_label.pack(anchor="w")
        status_label.bind("<Button-1>", select_item)
        
        # Error message if failed
        if item.error_message:
            error_label = ctk.CTkLabel(
                content,
                text=f"Error: {item.error_message}",
                font=("Arial", 9),
                text_color="red",
                anchor="w"
            )
            error_label.pack(anchor="w")
            error_label.bind("<Button-1>", select_item)
        
        # Folder path
        folder_label = ctk.CTkLabel(
            content,
            text=f"Folder: {item.download_folder}",
            font=("Arial", 9),
            text_color="gray",
            anchor="w"
        )
        folder_label.pack(anchor="w")
        folder_label.bind("<Button-1>", select_item)
        
        return item_frame
    
    def refresh_queue(self):
        """Refresh the queue display."""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get all queue items
        items = self.queue.get_all()
        
        # Create widgets for each item
        for item in items:
            item_widget = self.create_queue_item_widget(item)
            item_widget.pack(fill="x", pady=2)
        
        # Update stats
        stats = self.queue.get_stats()
        stats_text = (
            f"Total: {stats['total']} | "
            f"Pending: {stats['pending']} | "
            f"Downloading: {stats['downloading']} | "
            f"Paused: {stats['paused']} | "
            f"Completed: {stats['completed']} | "
            f"Failed: {stats['failed']}"
        )
        self.stats_label.configure(text=stats_text)
        
        # Update button states
        has_selection = self.selected_item_id is not None
        self.btn_move_up.configure(state="normal" if has_selection else "disabled")
        self.btn_move_down.configure(state="normal" if has_selection else "disabled")
        self.btn_pause.configure(state="normal" if has_selection else "disabled")
        self.btn_resume.configure(state="normal" if has_selection else "disabled")
        self.btn_cancel.configure(state="normal" if has_selection else "disabled")
    
    def move_up(self):
        """Move selected item up."""
        if self.selected_item_id:
            self.queue.move_up(self.selected_item_id)
    
    def move_down(self):
        """Move selected item down."""
        if self.selected_item_id:
            self.queue.move_down(self.selected_item_id)
    
    def pause_selected(self):
        """Pause selected item."""
        if self.selected_item_id:
            self.queue.pause(self.selected_item_id)
    
    def resume_selected(self):
        """Resume selected item."""
        if self.selected_item_id:
            self.queue.resume(self.selected_item_id)
    
    def cancel_selected(self):
        """Cancel selected item."""
        if self.selected_item_id:
            self.queue.update_status(self.selected_item_id, QueueItemStatus.CANCELLED)
    
    def clear_completed(self):
        """Clear all completed items."""
        count = self.queue.clear_completed()
        if count > 0:
            self.selected_item_id = None
