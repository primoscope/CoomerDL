import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr

        self.create_widgets()
        self.refresh_advanced_visibility() # Initial state check

    def create_widgets(self):
        # --- Title ---
        title_label = ctk.CTkLabel(
            self,
            text=self.tr("Welcome to CoomerDL"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 20))

        # --- URL Input ---
        url_frame = ctk.CTkFrame(self)
        url_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(url_frame, text=self.tr("Enter URL(s):"), font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,5))

        self.url_textbox = ctk.CTkTextbox(url_frame, height=100, wrap="none")
        self.url_textbox.pack(fill="x", padx=10, pady=5)
        self.url_textbox.insert("1.0", self.tr("Enter one URL per line..."))
        self.url_textbox.bind("<FocusIn>", self.on_url_focus)

        # Tip label
        ctk.CTkLabel(url_frame, text=self.tr("Tip: You can paste multiple URLs, one per line."), font=("Arial", 10), text_color="gray").pack(anchor="w", padx=10)

        # --- Folder Selection ---
        folder_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(folder_frame, text=self.tr("Download Folder:")).pack(side="left", padx=(0,10))

        self.folder_entry = ctk.CTkEntry(folder_frame, width=400)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.folder_entry.insert(0, self.app.download_folder)

        ctk.CTkButton(folder_frame, text=self.tr("Browse"), width=100, command=self.browse_folder).pack(side="left", padx=(10,0))

        # --- Advanced Options Expander ---
        self.advanced_frame_container = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_frame_container.pack(fill="x", padx=20, pady=5)

        self.advanced_toggle_btn = ctk.CTkButton(
            self.advanced_frame_container,
            text="▼ " + self.tr("Advanced Download Options"),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.toggle_advanced_options
        )
        # We pack this conditionally later or just pack it and hide the content frame

        self.advanced_options_frame = ctk.CTkFrame(self.advanced_frame_container)
        # Elements inside Advanced Options

        # Grid layout for advanced options
        self.advanced_options_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Format
        ctk.CTkLabel(self.advanced_options_frame, text="Format:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.format_combo = ctk.CTkComboBox(self.advanced_options_frame, values=["Best", "Video", "Audio Only"])
        self.format_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Quality
        ctk.CTkLabel(self.advanced_options_frame, text="Quality:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.quality_combo = ctk.CTkComboBox(self.advanced_options_frame, values=["Best", "1080p", "720p", "480p", "Worst"])
        self.quality_combo.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        # Container
        ctk.CTkLabel(self.advanced_options_frame, text="Container:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.container_combo = ctk.CTkComboBox(self.advanced_options_frame, values=["Auto", "mp4", "mkv", "webm", "mp3"])
        self.container_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Priority
        ctk.CTkLabel(self.advanced_options_frame, text="Priority:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.priority_combo = ctk.CTkComboBox(self.advanced_options_frame, values=["High", "Normal", "Low"])
        self.priority_combo.set("Normal")
        self.priority_combo.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # FFmpeg Args
        ctk.CTkLabel(self.advanced_options_frame, text="FFmpeg Args:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ffmpeg_args_entry = ctk.CTkEntry(self.advanced_options_frame, placeholder_text="-vcodec libx264 ...")
        self.ffmpeg_args_entry.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        # New Advanced Options
        # Bandwidth Limit
        ctk.CTkLabel(self.advanced_options_frame, text="Speed Limit (MB/s):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.speed_slider = ctk.CTkSlider(self.advanced_options_frame, from_=0, to=10, number_of_steps=20)
        self.speed_slider.set(0) # 0 = Unlimited
        self.speed_slider.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Date Range
        ctk.CTkLabel(self.advanced_options_frame, text="Date Range:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        date_frame = ctk.CTkFrame(self.advanced_options_frame, fg_color="transparent")
        date_frame.grid(row=3, column=3, padx=10, pady=5, sticky="ew")
        self.date_start = ctk.CTkEntry(date_frame, placeholder_text="YYYYMMDD", width=70)
        self.date_start.pack(side="left", padx=2)
        ctk.CTkLabel(date_frame, text="-").pack(side="left")
        self.date_end = ctk.CTkEntry(date_frame, placeholder_text="YYYYMMDD", width=70)
        self.date_end.pack(side="left", padx=2)

        # Proxy Toggle
        self.proxy_var = ctk.BooleanVar(value=False)
        self.proxy_check = ctk.CTkCheckBox(self.advanced_options_frame, text="Use Proxy", variable=self.proxy_var)
        self.proxy_check.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.advanced_options_frame, text="(Configure in Settings -> Network)", font=("Arial", 10), text_color="gray").grid(row=4, column=1, padx=0, pady=5, sticky="w")

        # --- Download Button ---
        self.download_btn = ctk.CTkButton(
            url_frame,
            text=self.tr("⬇ Download"),
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self.start_download
        )
        self.download_btn.pack(pady=10)

        # --- Quick Stats ---
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(stats_frame, text=self.tr("Quick Stats"), font=("Arial", 16, "bold")).pack(pady=10)

        grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=10)

        self.stat_total = self.create_stat_card(grid, "Total", "0", 0)
        self.stat_active = self.create_stat_card(grid, "Active", "0", 1)
        self.stat_completed = self.create_stat_card(grid, "Completed", "0", 2)
        self.stat_failed = self.create_stat_card(grid, "Failed", "0", 3)

        self.advanced_expanded = False

    def create_stat_card(self, parent, label, value, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(card, text=label, text_color="gray").pack(pady=(10,0))
        lbl = ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"))
        lbl.pack(pady=(0,10))
        return lbl

    def on_url_focus(self, event):
        txt = self.url_textbox.get("1.0", "end-1c").strip()
        if txt == self.tr("Enter one URL per line..."):
            self.url_textbox.delete("1.0", "end")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.app.download_folder = folder
            # Save logic should be in app

    def toggle_advanced_options(self):
        if self.advanced_expanded:
            self.advanced_options_frame.pack_forget()
            self.advanced_toggle_btn.configure(text="▼ " + self.tr("Advanced Download Options"))
            self.advanced_expanded = False
        else:
            self.advanced_options_frame.pack(fill="x", pady=(0, 10))
            self.advanced_toggle_btn.configure(text="▲ " + self.tr("Advanced Download Options"))
            self.advanced_expanded = True

    def refresh_advanced_visibility(self):
        """Called when settings change or page loads."""
        if self.app.advanced_mode:
            self.advanced_toggle_btn.pack(anchor="w", pady=(0,5))
            if self.advanced_expanded:
                self.advanced_options_frame.pack(fill="x", pady=(0, 10))
        else:
            self.advanced_toggle_btn.pack_forget()
            self.advanced_options_frame.pack_forget()

    def start_download(self):
        urls_text = self.url_textbox.get("1.0", "end-1c").strip()
        if not urls_text or urls_text == self.tr("Enter one URL per line..."):
            messagebox.showwarning("Warning", "Please enter at least one URL.")
            return

        urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
        folder = self.folder_entry.get().strip()

        if not folder:
            messagebox.showwarning("Warning", "Please select a download folder.")
            return

        # Prepare Options
        from app.models.download_queue import QueuePriority

        priority_map = {"High": QueuePriority.HIGH, "Normal": QueuePriority.NORMAL, "Low": QueuePriority.LOW}
        priority = priority_map.get(self.priority_combo.get(), QueuePriority.NORMAL) if self.app.advanced_mode else QueuePriority.NORMAL

        # Add to Queue via App
        count = 0
        for url in urls:
            self.app.download_queue.add(
                url=url,
                download_folder=folder,
                priority=priority
                # We could store advanced options (format, container) in queue metadata if supported
            )
            count += 1

        messagebox.showinfo("Success", f"Added {count} items to queue.")
        self.url_textbox.delete("1.0", "end")

    def log_message(self, msg):
        # We could show toast or small log line here
        pass
