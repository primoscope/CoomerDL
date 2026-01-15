from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.models.download_queue import QueueItemStatus

# Constants
QUEUE_REFRESH_INTERVAL_MS = 2000  # Auto-refresh interval in milliseconds

class QueuePage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr
        self.queue = app.download_queue
        self._refresh_scheduled = False  # Track scheduled refresh to prevent leaks

        self.create_widgets()
        self.refresh_queue_display()

        # Auto-refresh loop
        self.refresh_loop()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header, text=self.tr("Download Queue"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")

        ctk.CTkButton(controls, text="Process Queue", command=self.process_queue).pack(side="left", padx=5)
        ctk.CTkButton(controls, text="Clear Completed", command=self.clear_completed, fg_color="gray").pack(side="left", padx=5)

        # Queue List
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Queue Items")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh_loop(self):
        if self.winfo_exists():
            self.refresh_queue_display()
            self._refresh_scheduled = True
            self.after(QUEUE_REFRESH_INTERVAL_MS, self.refresh_loop)
        else:
            self._refresh_scheduled = False

    def refresh_queue_display(self):
        # This is a naive implementation: clearing and redrawing.
        # For production, we should update existing widgets.
        # But given the complexity limit, I'll stick to naive for now or optimize slightly.

        # Get all items
        items = self.queue.get_all()

        # Clear (naive)
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not items:
            ctk.CTkLabel(self.scroll_frame, text="Queue is empty", text_color="gray").pack(pady=20)
            return

        for item in items:
            self.create_item_card(item)

    def create_item_card(self, item):
        card = ctk.CTkFrame(self.scroll_frame)
        card.pack(fill="x", pady=2, padx=5)

        # Status Icon/Color
        color_map = {
            QueueItemStatus.PENDING: "gray",
            QueueItemStatus.DOWNLOADING: "blue",
            QueueItemStatus.COMPLETED: "green",
            QueueItemStatus.FAILED: "red",
            QueueItemStatus.CANCELLED: "orange",
            QueueItemStatus.PAUSED: "yellow"
        }
        color = color_map.get(item.status, "gray")

        ctk.CTkLabel(card, text="●", text_color=color, font=("Arial", 16)).pack(side="left", padx=10)

        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        url_short = (item.url[:60] + '..') if len(item.url) > 60 else item.url
        ctk.CTkLabel(info, text=url_short, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=f"{item.status.value} | Priority: {item.priority.name}", font=("Arial", 10), text_color="gray", anchor="w").pack(fill="x")

        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=5)

        if item.status in [QueueItemStatus.PENDING, QueueItemStatus.PAUSED]:
            ctk.CTkButton(actions, text="✕", width=30, height=30, fg_color="transparent", text_color="red", command=lambda: self.remove_item(item.id)).pack(side="left")

    def process_queue(self):
        """
        Handler for the "Process Queue" action.

        Real queue processing logic is not implemented here yet. To avoid
        misleading users, we explicitly inform them that this feature is
        currently unavailable instead of pretending to start processing.
        """
        messagebox.showinfo(
            "Feature unavailable",
            "Processing the queue is not available in this version.\n\n"
            "You can still manage queued items (remove items or clear completed), "
            "but starting downloads from this screen has not been implemented yet."
        )

    def remove_item(self, item_id):
        self.queue.remove(item_id)
        self.refresh_queue_display()

    def clear_completed(self):
        self.queue.clear_completed()
        self.refresh_queue_display()
