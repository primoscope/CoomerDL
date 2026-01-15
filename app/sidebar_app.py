from __future__ import annotations

import customtkinter as ctk
import os
import sys
import json
from typing import Optional, Dict, Any, Callable

# Import core components (same as ImageDownloaderApp)
from app.settings_window import SettingsWindow
from downloader.downloader import Downloader
from app.models.download_queue import DownloadQueue

# Constants
VERSION = "V2.0.0 (UI Overhaul)"

class SidebarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Basic Setup
        self.title(f"CoomerDL {VERSION}")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        if sys.platform == "win32":
            try:
                self.iconbitmap("resources/img/window.ico")
            except (FileNotFoundError, Exception):
                pass

        # 1. Initialize Settings & Translations (Core)
        # We use SettingsWindow logic to load settings, but we might display it differently
        self.settings_helper = SettingsWindow(
            self,
            lambda *args, **kwargs: self.tr(*args, **kwargs),
            self.load_translations,
            self.update_ui_texts,
            self.save_language_preference,
            VERSION,
            None, # Downloader set later
            lambda x: None # check_update placeholder
        )
        self.settings = self.settings_helper.settings

        # Load Language
        lang = self.load_language_preference()
        self.load_translations(lang)

        # 2. Initialize Core Logic (Queue, Downloader)
        self.download_queue = DownloadQueue(
            on_change=self.on_queue_changed,
            persist_file="resources/config/download_queue.json"
        )

        self.download_folder = self.load_download_folder()
        self.default_downloader = Downloader(
            download_folder=self.download_folder,
            max_workers=self.settings.get('max_downloads', 3),
            log_callback=self.log_message,
            update_progress_callback=self.update_progress,
            update_global_progress_callback=self.update_global_progress,
            tr=self.tr
        )
        self.settings_helper.downloader = self.default_downloader # Link back

        self.active_downloader = None
        
        # Validate and load advanced_mode setting
        advanced_mode_value = self.settings.get('advanced_mode', False)
        if isinstance(advanced_mode_value, bool):
            self.advanced_mode = advanced_mode_value
        else:
            # Fallback to a safe default if the stored value is not a boolean
            self.advanced_mode = False

        # 3. Setup UI Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # Spacer push down

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CoomerDL", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.nav_buttons = {}
        self.create_nav_button("Home", self.show_home, 1, icon_name="home")
        self.create_nav_button("Queue", self.show_queue, 2, icon_name="list")
        self.create_nav_button("History", self.show_history, 3, icon_name="history")
        self.create_nav_button("Converter", self.show_converter, 4, icon_name="movie")
        self.create_nav_button("Settings", self.show_settings, 5, icon_name="settings")
        self.create_nav_button("Help", self.show_help, 6, icon_name="help")

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Pages Cache
        self.pages = {}
        self.current_page = None

        # 4. Initialize Default Page
        self.show_home()

    def create_nav_button(self, text, command, row, icon_name=None):
        btn = ctk.CTkButton(
            self.sidebar_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=text,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=command
        )
        btn.grid(row=row, column=0, sticky="ew")
        self.nav_buttons[text] = btn

    def select_nav_button(self, name):
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def show_page(self, name, page_class, **kwargs):
        self.select_nav_button(name)

        # Hide current
        if self.current_page:
            self.current_page.pack_forget()

        # Create or Get
        if name not in self.pages:
            try:
                self.pages[name] = page_class(parent=self.content_frame, app=self, **kwargs)
            except Exception as e:
                # Fallback for when pages are not yet implemented
                print(f"Error loading {name}: {e}")
                self.pages[name] = ctk.CTkLabel(self.content_frame, text=f"Error loading {name}\n{e}")

        self.current_page = self.pages[name]
        self.current_page.pack(fill="both", expand=True)

    # --- Navigation Callbacks ---
    def show_home(self):
        # We will import the class locally to avoid circular imports later or import errors now
        try:
            from app.window.pages.home import HomePage
            self.show_page("Home", HomePage)
        except ImportError:
            self.show_placeholder("Home")

    def show_queue(self):
        try:
            from app.window.pages.queue import QueuePage
            self.show_page("Queue", QueuePage)
        except ImportError:
            self.show_placeholder("Queue")

    def show_history(self):
        try:
            from app.window.pages.history import HistoryPage
            self.show_page("History", HistoryPage)
        except ImportError:
            self.show_placeholder("History")

    def show_converter(self):
        try:
            from app.window.pages.converter import ConverterPage
            self.show_page("Converter", ConverterPage)
        except ImportError:
            self.show_placeholder("Converter")

    def show_settings(self):
        try:
            from app.window.pages.settings import SettingsPage
            self.show_page("Settings", SettingsPage)
        except ImportError:
            self.show_placeholder("Settings")

    def show_help(self):
        try:
            from app.window.pages.help import HelpPage
            self.show_page("Help", HelpPage)
        except ImportError:
            self.show_placeholder("Help")

    def show_placeholder(self, name):
        self.select_nav_button(name)
        if self.current_page: self.current_page.pack_forget()

        if name not in self.pages:
            frame = ctk.CTkFrame(self.content_frame)
            ctk.CTkLabel(frame, text=f"{name} Page (Coming Soon)", font=("Arial", 20)).pack(expand=True)
            self.pages[name] = frame

        self.current_page = self.pages[name]
        self.current_page.pack(fill="both", expand=True)

    # --- Core Logic Helpers ---
    def load_language_preference(self):
        try:
            with open('resources/config/languages/save_language/language_config.json', 'r') as f:
                return json.load(f).get('language', 'en')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return 'en'

    def save_language_preference(self, lang_code):
        os.makedirs('resources/config/languages/save_language', exist_ok=True)
        with open('resources/config/languages/save_language/language_config.json', 'w') as f:
            json.dump({'language': lang_code}, f)

    def load_translations(self, lang):
        path = "resources/config/languages/translations.json"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                all_trans = json.load(f)
                self.translations = {k: v.get(lang, k) for k, v in all_trans.items()}
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.translations = {}

    def tr(self, text, **kwargs):
        res = self.translations.get(text, text)
        if kwargs:
            res = res.format(**kwargs)
        return res

    def update_ui_texts(self):
        # Refresh current page if needed
        if self.current_page:
            if hasattr(self.current_page, 'refresh_advanced_visibility'):
                self.current_page.refresh_advanced_visibility()
            if hasattr(self.current_page, 'refresh_tabs'):
                self.current_page.refresh_tabs()

    def load_download_folder(self):
        path = 'resources/config/download_path/download_folder.json'
        try:
            with open(path, 'r') as f:
                return json.load(f).get('download_folder', '')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return ''

    def log_message(self, msg):
        # Broadcast log to active page if it has a log viewer
        import logging
        logging.info(f"[CoomerDL] {msg}")
        if hasattr(self.current_page, 'log_message'):
            self.current_page.log_message(msg)

    def update_progress(self, *args, **kwargs):
        """
        Callback to update per-item download progress.
        Delegates to the current page if it implements `update_progress`.
        """
        if hasattr(self, "current_page") and hasattr(self.current_page, "update_progress"):
            self.current_page.update_progress(*args, **kwargs)

    def update_global_progress(self, *args, **kwargs):
        """
        Callback to update overall/global download progress.
        Delegates to the current page if it implements `update_global_progress`.
        """
        if hasattr(self, "current_page") and hasattr(self.current_page, "update_global_progress"):
            self.current_page.update_global_progress(*args, **kwargs)

    def on_queue_changed(self):
        # Update badge on queue button?
        pass

if __name__ == "__main__":
    app = SidebarApp()
    app.mainloop()
