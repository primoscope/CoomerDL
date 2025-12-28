import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import webbrowser
import os
import sys

# Import core views and panels
from app.ui import ImageDownloaderApp  # We will use components from the original file

# We will reuse the logic from ImageDownloaderApp but wrap it in a frame
# For now, to ensure compatibility, we will essentially embed the "Downloader" logic
# into a Frame instead of the root window.

class SidebarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("CoomerDL Universal")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Grid Configuration (Sidebar + Content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1)  # Content expands

        # Load Resources (Icons, etc)
        self.load_resources()

        # Initialize Logic (Settings, Queue, etc)
        self.init_core_logic()

        # Create Layout
        self.create_sidebar()
        self.create_content_area()

        # Show Default View
        self.show_view("downloader")

        # Handle Close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Check for active downloads in the embedded app
        if hasattr(self, 'downloader_app') and self.downloader_app:
            # We can use the existing logic if we can access it, or implement our own check
            if self.downloader_app.is_download_active():
                if not self.downloader_app.on_app_close():
                    return # Cancel close

        # Stop monitoring threads
        if hasattr(self, 'clipboard_monitor'):
            self.clipboard_monitor.stop()

        self.destroy()
        # Ensure process exit
        try:
            import psutil
            current_process = psutil.Process(os.getpid())
            for handler in current_process.children(recursive=True):
                handler.kill()
            current_process.kill()
        except:
            pass

    def load_resources(self):
        # Load generic icons (placeholders if real ones missing)
        self.icons = {}
        # In a real impl, we would load SVG/PNGs here

    def init_core_logic(self):
        from app.utils.clipboard_monitor import ClipboardMonitor
        self.clipboard_monitor = ClipboardMonitor(self.on_clipboard_url)

    def on_clipboard_url(self, url):
        # Callback when clipboard has a URL
        if hasattr(self, 'downloader_app') and self.downloader_app:
            # We need to update the input field in the downloader view
            # Since this is called from a thread, we use after()
            self.after(0, lambda: self.update_downloader_input(url))

    def update_downloader_input(self, url):
        # Switch to downloader view if not active
        self.show_view("downloader")

        # Update entry
        if hasattr(self.downloader_app, 'url_entry'):
            self.downloader_app.url_entry.delete(0, tk.END)
            self.downloader_app.url_entry.insert(0, url)

            # Flash or notify
            # messagebox.showinfo("Link Detected", f"Found link: {url}") # Too intrusive
            pass

    def toggle_monitor(self):
        if self.monitor_switch.get() == 1:
            self.clipboard_monitor.start()
        else:
            self.clipboard_monitor.stop()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Spacer

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CoomerDL", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.btn_downloader = self.create_nav_button("Downloader", "downloader", 1)
        self.btn_queue = self.create_nav_button("Queue", "queue", 2)
        self.btn_history = self.create_nav_button("History", "history", 3)
        self.btn_settings = self.create_nav_button("Settings", "settings", 4)

        # Spacer (row 5 is weight 1)

        # Bottom Actions
        self.monitor_switch = ctk.CTkSwitch(self.sidebar_frame, text="Clipboard Monitor", command=self.toggle_monitor)
        self.monitor_switch.grid(row=6, column=0, padx=20, pady=10, sticky="s")

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text="About", fg_color="transparent", border_width=1, command=self.show_about)
        self.btn_about.grid(row=7, column=0, padx=20, pady=20, sticky="s")

    def create_nav_button(self, text, view_name, row):
        btn = ctk.CTkButton(self.sidebar_frame, corner_radius=0, height=40, border_spacing=10, text=text,
                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                            anchor="w", command=lambda: self.show_view(view_name))
        btn.grid(row=row, column=0, sticky="ew")
        return btn

    def create_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # We will pack different frames into this content_frame
        self.views = {}

        # Initialize Views
        self.views["downloader"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["queue"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["history"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.views["settings"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")

    def show_view(self, view_name):
        # Highlight Button
        self.highlight_button(view_name)

        # Hide all views
        for view in self.views.values():
            view.pack_forget()

        # Show selected view
        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True)

            # Lazy Load content if empty
            if len(self.views[view_name].winfo_children()) == 0:
                self.load_view_content(view_name)

    def highlight_button(self, view_name):
        # Reset colors
        for btn in [self.btn_downloader, self.btn_queue, self.btn_history, self.btn_settings]:
            btn.configure(fg_color="transparent")

        # Highlight selected
        if view_name == "downloader": self.btn_downloader.configure(fg_color=("gray75", "gray25"))
        if view_name == "queue": self.btn_queue.configure(fg_color=("gray75", "gray25"))
        if view_name == "history": self.btn_history.configure(fg_color=("gray75", "gray25"))
        if view_name == "settings": self.btn_settings.configure(fg_color=("gray75", "gray25"))

    def load_view_content(self, view_name):
        parent = self.views[view_name]
        if view_name == "downloader":
            self.build_downloader_view(parent)
        elif view_name == "queue":
            ctk.CTkLabel(parent, text="Download Queue (Use the Queue Manager from Menu for now)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "history":
            ctk.CTkLabel(parent, text="History View (Coming Soon)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "settings":
             ctk.CTkLabel(parent, text="Settings are currently in a popup window.", font=("Arial", 20)).pack(pady=50)

    def build_downloader_view(self, parent):
        # Embed the refactored ImageDownloaderApp (now a Frame)
        self.downloader_app = ImageDownloaderApp(parent)
        self.downloader_app.pack(fill="both", expand=True)

    def show_about(self):
        pass

if __name__ == "__main__":
    app = SidebarApp()
    app.mainloop()
