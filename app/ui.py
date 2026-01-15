from __future__ import annotations

import datetime
import json
import queue
import sys
import re
import os
import time
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional, List, Dict, Any, Tuple, Callable
from urllib.parse import ParseResult, parse_qs, urlparse
import webbrowser
import requests
from PIL import Image, ImageTk
import customtkinter as ctk
import psutil
import functools
import subprocess

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    dnd_available = True
except ImportError:
    dnd_available = False

#from app.patch_notes import PatchNotes
from app.settings_window import SettingsWindow
#from app.user_panel import UserPanel
from app.about_window import AboutWindow
from downloader.downloader import Downloader
from app.progress_manager import ProgressManager
from app.donors import DonorsModal
from app.window.input_panel import InputPanel
from app.window.options_panel import OptionsPanel
from app.window.action_panel import ActionPanel
from app.window.log_panel import LogPanel
from app.window.progress_panel import ProgressPanel
from app.window.status_bar import StatusBar
from app.controllers.download_controller import DownloadController

VERSION = "V0.8.12"
MAX_LOG_LINES = 1000  # Set to reasonable default to prevent crashes

# Application class
class ImageDownloaderApp(ctk.CTk):
    def __init__(self) -> None:
        self.errors: List[str] = []
        self._log_buffer: List[str] = []
        self.github_stars = 0
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()
        self.version = VERSION
        self.title(f"Downloader [{VERSION}]")
        
        # Setup window
        self.setup_window()
        
        # Settings window
        self.settings_window = SettingsWindow(
            self,
            self.tr,
            self.load_translations,
            self.update_ui_texts,
            self.save_language_preference,
            VERSION,
            None,  # Por ahora, no se pasa ningún downloader
            self.check_for_new_version,
            on_settings_changed=self.apply_runtime_settings
        )

        self.all_logs = []  # Lista para almacenar todos los logs

        # About window
        self.about_window = AboutWindow(self, self.tr, VERSION)  # Inicializa AboutWindow
        
        self.extras_window = None

        # Load settings
        self.settings = self.settings_window.load_settings()
        
        # Language preferences
        lang = self.load_language_preference()
        self.load_translations(lang)
        self.image_downloader = None

        # Patch notes
        #self.patch_notes = PatchNotes(self, self.tr)

        self.progress_bars = {}
        
        # Obtener el número de estrellas de GitHub
        self.github_stars = self.get_github_stars("emy69", "CoomerDL")

        # Cargar el icono de GitHub
        self.github_icon = self.load_github_icon()
        
        self.autoscroll_logs_var = tk.BooleanVar(value=False) 

        # Initialize download queue
        from app.models.download_queue import DownloadQueue
        self.download_queue = DownloadQueue(
            on_change=self.on_queue_changed,
            persist_file="resources/config/download_queue.json"
        )

        # Queue processing flags/state
        self._process_queue_all_active = False
        self._queue_progress_last_update = 0.0
        self._queue_progress_throttle_seconds = 0.25

        # Initialize UI
        self.initialize_ui()
        
        self.update_ui_texts()  

        self.update_queue = queue.Queue()
        self.check_update_queue()
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

        self.download_start_time = None
        self.errors = []
        self.warnings = []
        
        # Load all settings with defaults from the settings object
        self.max_downloads = self.settings.get('max_downloads', 3)
        max_retries_setting = self.settings.get('max_retries', 3)
        retry_interval_setting = self.settings.get('retry_interval', 2.0)
        folder_structure_setting = self.settings.get('folder_structure', 'default')
        
        # Load network settings (proxy, user agent)
        network_settings = self.settings.get('network', {})
        proxy_type = network_settings.get('proxy_type', 'none')
        proxy_url = network_settings.get('proxy_url', '')
        user_agent = network_settings.get('user_agent', None)
        
        # Load download folder
        self.download_folder = self.load_download_folder() 
        if self.download_folder:
            self.input_panel.set_download_folder(self.download_folder)

        self.default_downloader = Downloader(
            download_folder=self.download_folder,
            max_workers=self.max_downloads,
            log_callback=self.add_log_message_safe,
            update_progress_callback=self.update_progress,
            update_global_progress_callback=self.update_global_progress,
            tr=self.tr,
            retry_interval=retry_interval_setting,
            folder_structure=folder_structure_setting,
            max_retries=max_retries_setting,
            proxy_type=proxy_type,
            proxy_url=proxy_url,
            user_agent=user_agent
        )
        
        self.settings_window.downloader = self.default_downloader

        self.active_downloader = None  # Initialize active_downloader

        # Cargar iconos redimensionados
        self.icons = {
            'image': self.load_and_resize_image('resources/img/iconos/ui/image_icon.png', (40, 40)),
            'video': self.load_and_resize_image('resources/img/iconos/ui/video.png', (40, 40)),
            'zip': self.load_and_resize_image('resources/img/iconos/ui/file-zip.png', (40, 40)),
            'default': self.load_and_resize_image('resources/img/iconos/ui/default_icon.png', (40, 40))
        }

        # Progress manager
        self.progress_manager = ProgressManager(
            root=self,
            icons=self.icons,
            footer_speed_label=self.status_bar.footer_speed_label,
            footer_eta_label=self.status_bar.footer_eta_label,
            progress_bar=self.progress_panel.progress_bar,
            progress_percentage=self.progress_panel.progress_percentage
        )
        
        # Check for new version on startup
        threading.Thread(target=self.check_for_new_version, args=(True,)).start()

    # Application close event
    def on_app_close(self) -> None:
        if self.is_download_active() and not self.active_downloader.cancel_requested:
            # Mostrar advertencia si hay una descarga activa
            messagebox.showwarning(
                self.tr("Descarga Activa"),
                self.tr("Hay una descarga en progreso. Por favor, cancela la descarga antes de cerrar.")
            )
        else:
            self.destroy()

    def is_download_active(self) -> bool:
        return self.active_downloader is not None
    
    def close_program(self) -> None:
        # Cierra todas las ventanas y termina el proceso principal
        self.destroy()
        # Matar el proceso actual (eliminar del administrador de tareas)
        current_process = psutil.Process(os.getpid())
        for handler in current_process.children(recursive=True):
            handler.kill()
        current_process.kill()
    
    # Save and load language preferences
    def save_language_preference(self, language_code: str) -> None:
        config = {'language': language_code}
        with open('resources/config/languages/save_language/language_config.json', 'w') as config_file:
            json.dump(config, config_file)
        self.load_translations(language_code)
        self.update_ui_texts()
    
    def load_language_preference(self) -> str:
        try:
            with open('resources/config/languages/save_language/language_config.json', 'r') as config_file:
                config = json.load(config_file)
                return config.get('language', 'en')
        except FileNotFoundError:
            return 'en'

    # Load translations
    def load_translations(self, lang: str) -> None:
        path = "resources/config/languages/translations.json"
        with open(path, 'r', encoding='utf-8') as file:
            all_translations = json.load(file)
            self.translations = {key: value.get(lang, key) for key, value in all_translations.items()}
    
    def tr(self, text: str, **kwargs: Any) -> str:
        translated_text = self.translations.get(text, text)
        if kwargs:
            translated_text = translated_text.format(**kwargs)
        return translated_text
    
    def build_download_options(self) -> Any:
        """
        Build DownloadOptions from current settings.
        
        Returns:
            DownloadOptions configured from UI and settings
        """
        from downloader.base import DownloadOptions
        
        # Get network settings
        network_settings = self.settings.get('network', {})
        
        # Get filter settings
        filter_settings = self.settings.get('filters', {})
        
        # Build excluded extensions set
        excluded_extensions = set()
        if filter_settings.get('exclude_webm', False):
            excluded_extensions.add('.webm')
        if filter_settings.get('exclude_gif', False):
            excluded_extensions.add('.gif')
        if filter_settings.get('exclude_webp', False):
            excluded_extensions.add('.webp')
        if filter_settings.get('exclude_zip', False):
            excluded_extensions.add('.zip')
        if filter_settings.get('exclude_rar', False):
            excluded_extensions.add('.rar')
        
        # Build options
        options = DownloadOptions(
            download_images=self.download_images_check.get() if hasattr(self, 'download_images_check') else True,
            download_videos=self.download_videos_check.get() if hasattr(self, 'download_videos_check') else True,
            download_compressed=self.download_compressed_check.get() if hasattr(self, 'download_compressed_check') else True,
            download_documents=True,  # Always download documents
            max_retries=network_settings.get('max_retries', 3),
            retry_interval=float(network_settings.get('base_delay', 2.0)),
            chunk_size=1048576,  # 1MB
            # Note: 'timeout' is deprecated, use connection_timeout and read_timeout
            min_file_size=int(filter_settings.get('min_file_size_mb', 0)) * 1024 * 1024,
            max_file_size=int(filter_settings.get('max_file_size_mb', 0)) * 1024 * 1024,
            date_from=filter_settings.get('date_from', '') or None,
            date_to=filter_settings.get('date_to', '') or None,
            excluded_extensions=excluded_extensions,
            proxy_type=network_settings.get('proxy_type', 'none'),
            proxy_url=network_settings.get('proxy_url', ''),
            user_agent=network_settings.get('user_agent', None),
            bandwidth_limit_kbps=network_settings.get('bandwidth_limit_kbps', 0),
            connection_timeout=network_settings.get('connection_timeout', 30),
            read_timeout=network_settings.get('read_timeout', 60),
        )
        
        return options
    
    def apply_runtime_settings(self, new_settings: Dict[str, Any]) -> None:
        """
        Se llama cuando se guardan cambios en Settings.
        Aplica cambios en caliente (sin reiniciar la app).
        """
        try:
            self.settings = new_settings

            # Max downloads (concurrencia)
            self.max_downloads = int(new_settings.get("max_downloads", 3) or 3)

            # Downloader principal
            if hasattr(self, "default_downloader") and self.default_downloader:
                dd = self.default_downloader
                dd.max_workers = self.max_downloads
                dd.folder_structure = new_settings.get("folder_structure", "default")

                dd.size_filter_enabled = bool(new_settings.get("size_filter_enabled", False))
                dd.min_size = float(new_settings.get("min_size_mb", 0) or 0) * 1024 * 1024
                dd.max_size = float(new_settings.get("max_size_mb", 0) or 0) * 1024 * 1024

                # modo de nombre de archivo (si lo usas)
                try:
                    dd.file_naming_mode = int(new_settings.get("file_naming_mode", 0) or 0)
                except Exception:
                    pass

                # reintentos por archivo (si tu downloader lo soporta)
                try:
                    dd.download_retry_attempts = int(new_settings.get("download_retry_attempts", 3) or 3)
                except Exception:
                    pass
                
            if hasattr(self, "refresh_download_settings"):
                try:
                    self.refresh_download_settings()
                except Exception:
                    pass

            self.add_log_message_safe("Settings applied.")
        except Exception as e:
            try:
                self.add_log_message_safe(f"Error applying settings: {e}")
            except Exception:
                pass


    # Window setup
    def setup_window(self) -> None:
        window_width, window_height = 1000, 600
        center_x = int((self.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((self.winfo_screenheight() / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        if sys.platform == "win32":
            self.iconbitmap("resources/img/window.ico")

    # Initialize UI components
    def initialize_ui(self) -> None:

        # Crear la barra de menú personalizada
        self.menu_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.menu_bar.pack(side="top", fill="x")

        # Añadir botones al menú
        self.create_custom_menubar()

        # Update alert frame (initially hidden)
        self.update_alert_frame = ctk.CTkFrame(self, fg_color="#4CAF50", corner_radius=0) # Green background
        self.update_alert_frame.pack(side="top", fill="x")
        self.update_alert_frame.pack_forget() # Hide initially

        self.update_alert_label = ctk.CTkLabel(self.update_alert_frame, text="", text_color="white", font=("Arial", 12, "bold"))
        self.update_alert_label.pack(side="left", padx=10, pady=5)

        self.update_download_button = ctk.CTkButton(self.update_alert_frame, text=self.tr("Download Now"), command=self.open_latest_release, fg_color="#388E3C", hover_color="#2E7D32")
        self.update_download_button.pack(side="right", padx=10, pady=5)

        # Input panel
        self.input_panel = InputPanel(
            self,
            tr=self.tr,
            on_folder_change=self.on_folder_selected
        )
        self.input_panel.pack(fill='x', padx=20, pady=20)

        # Options panel
        self.options_panel = OptionsPanel(self, tr=self.tr)
        self.options_panel.pack(pady=10, fill='x', padx=20)

        # Action panel
        self.action_panel = ActionPanel(
            self,
            tr=self.tr,
            on_download=self.start_download,
            on_cancel=self.cancel_download,
            on_add_to_queue=self.add_to_queue,
            autoscroll_var=self.autoscroll_logs_var
        )
        self.action_panel.pack(pady=10, fill='x', padx=20)

        # Log panel
        self.log_panel = LogPanel(
            self,
            tr=self.tr,
            autoscroll_var=self.autoscroll_logs_var,
            width=590,
            height=200
        )
        self.log_panel.pack(pady=(10, 0), padx=20, fill='both', expand=True)

        # Progress panel
        self.progress_panel = ProgressPanel(
            self,
            tr=self.tr,
            on_toggle_details=self.toggle_progress_details
        )
        self.progress_panel.pack(pady=(0, 10), fill='x', padx=20)

        self.progress_details_frame = ctk.CTkFrame(self)
        self.progress_details_frame.place_forget()

        # Context menu for URL entry
        self.context_menu = tk.Menu(self.input_panel.get_url_entry_widget(), tearoff=0)
        self.context_menu.add_command(label=self.tr("Copiar"), command=self.copy_to_clipboard)
        self.context_menu.add_command(label=self.tr("Pegar"), command=self.paste_from_clipboard)
        self.context_menu.add_command(label=self.tr("Cortar"), command=self.cut_to_clipboard)

        self.input_panel.get_url_entry_widget().bind("<Button-3>", self.show_context_menu)
        self.bind("<Button-1>", self.on_click)

        # Status bar (footer)
        self.status_bar = StatusBar(self, tr=self.tr)
        self.status_bar.pack(side="bottom", fill="x")

        # Actualizar textos después de inicializar la UI
        self.update_ui_texts()

    # Update UI texts
    def update_ui_texts(self) -> None:

        # Actualizar textos de los botones del menú
        for widget in self.menu_bar.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                text = widget.cget("text")
                if text.strip() in ["Archivo", "Ayuda", "Donaciones", "About", "Patreons"]:
                    widget.configure(text=self.tr(text.strip()))

        # Si los menús están abiertos, recrearlos para actualizar los textos
        if self.archivo_menu_frame and self.archivo_menu_frame.winfo_exists():
            self.archivo_menu_frame.destroy()
            self.toggle_archivo_menu()

        # Update modular panel texts
        self.input_panel.update_texts()
        self.options_panel.update_texts()
        self.action_panel.update_texts()
        
        self.title(self.tr(f"Downloader [{VERSION}]"))
        self.update_download_button.configure(text=self.tr("Download Now"))

    
    def on_folder_selected(self, folder_path: str) -> None:
        """Callback when folder is selected via InputPanel."""
        self.download_folder = folder_path
        self.save_download_folder(folder_path)
    
    def open_download_folder(self, event: Optional[Any] = None) -> None:
        # This method is now handled by InputPanel, but kept for backward compatibility
        pass
    
    # Property accessors for backward compatibility with existing code
    @property
    def url_entry(self) -> Any:
        """Access URL entry widget from InputPanel."""
        return self.input_panel.url_entry
    
    @property
    def download_images_check(self) -> Any:
        """Access download images checkbox from OptionsPanel."""
        return self.options_panel.download_images_check
    
    @property
    def download_videos_check(self) -> Any:
        """Access download videos checkbox from OptionsPanel."""
        return self.options_panel.download_videos_check
    
    @property
    def download_compressed_check(self) -> Any:
        """Access download compressed checkbox from OptionsPanel."""
        return self.options_panel.download_compressed_check
    
    @property
    def download_documents_check(self) -> Any:
        """Access download documents checkbox from OptionsPanel."""
        return self.options_panel.download_documents_check
    
    @property
    def download_button(self) -> Any:
        """Access download button from ActionPanel."""
        return self.action_panel.download_button
    
    @property
    def cancel_button(self) -> Any:
        """Access cancel button from ActionPanel."""
        return self.action_panel.cancel_button
    
    @property
    def log_textbox(self) -> Any:
        """Access log textbox from LogPanel."""
        return self.log_panel


    def on_click(self, event: Any) -> None:
        # Obtener la lista de widgets que no deben cerrar el menú al hacer clic
        widgets_to_ignore: List[tk.Widget] = [self.menu_bar]

        # Añadir los frames de los menús desplegables si existen
        for frame in [self.archivo_menu_frame, self.ayuda_menu_frame, self.donaciones_menu_frame]:
            if frame and frame.winfo_exists():
                widgets_to_ignore.append(frame)
                widgets_to_ignore.extend(self.get_all_children(frame))

        # Si el widget en el que se hizo clic no es ninguno de los que debemos ignorar, cerramos los menús
        if event.widget not in widgets_to_ignore:
            self.close_all_menus()

    def get_all_children(self, widget: tk.Widget) -> List[tk.Widget]:
        children = widget.winfo_children()
        all_children = list(children)
        for child in children:
            all_children.extend(self.get_all_children(child))
        return all_children

    def create_custom_menubar(self) -> None:
        # Botón Archivo
        archivo_button = ctk.CTkButton(
            self.menu_bar,
            text=self.tr("Archivo"),
            width=80,
            fg_color="transparent",
            hover_color="gray25",
            command=self.toggle_archivo_menu
        )
        archivo_button.pack(side="left")
        archivo_button.bind("<Button-1>", lambda e: "break")

        # Botón About
        about_button = ctk.CTkButton(
            self.menu_bar,
            text=self.tr("About"),
            width=80,
            fg_color="transparent",
            hover_color="gray25",
            command=self.about_window.show_about 
        )
        about_button.pack(side="left")
        about_button.bind("<Button-1>", lambda e: "break")

        # Botón Donors
        donors_button = ctk.CTkButton(
            self.menu_bar,
            text=self.tr("Patreons"),
            width=80,
            fg_color="transparent",
            hover_color="gray25",
            command=self.show_donors_modal
        )
        donors_button.pack(side="left")
        donors_button.bind("<Button-1>", lambda e: "break")
        
        # Botón Queue
        self.queue_button = ctk.CTkButton(
            self.menu_bar,
            text="📋 " + self.tr("Queue"),
            width=80,
            fg_color="transparent",
            hover_color="gray25",
            command=self.show_queue_manager
        )
        self.queue_button.pack(side="left")
        self.queue_button.bind("<Button-1>", lambda e: "break")

        # Inicializar variables para los menús desplegables
        self.archivo_menu_frame = None
        self.ayuda_menu_frame = None
        self.donaciones_menu_frame = None

        # Función para cambiar el fondo al pasar el ratón
        def on_enter(event, frame):
            frame.configure(fg_color="gray25")

        def on_leave(event, frame):
            frame.configure(fg_color="transparent")

        # Añadir el icono de GitHub y el contador de estrellas
        if self.github_icon:
            resized_github_icon = self.github_icon.resize((16, 16), Image.Resampling.LANCZOS)
            resized_github_icon = ctk.CTkImage(resized_github_icon)
            github_frame = ctk.CTkFrame(self.menu_bar,cursor="hand2", fg_color="transparent", corner_radius=5)
            github_frame.pack(side="right", padx=5)
            github_label = ctk.CTkLabel(
                github_frame,
                image=resized_github_icon,
                text=f" Star {self.github_stars}",
                compound="left",
                font=("Arial", 12)
            )
            github_label.pack(padx=5, pady=5)
            github_frame.bind("<Enter>", lambda e: on_enter(e, github_frame))
            github_frame.bind("<Leave>", lambda e: on_leave(e, github_frame))
            github_label.bind("<Enter>", lambda e: on_enter(e, github_frame))
            github_label.bind("<Leave>", lambda e: on_leave(e, github_frame))
            github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/primoscope/CoomerDL"))
    
    def show_donors_modal(self) -> None:
        donors_modal = DonorsModal(self, self.tr)
        donors_modal.focus_set()

    def toggle_archivo_menu(self) -> None:
        if self.archivo_menu_frame and self.archivo_menu_frame.winfo_exists():
            self.archivo_menu_frame.destroy()
        else:
            self.close_all_menus()
            self.archivo_menu_frame = self.create_menu_frame([
                (self.tr("Configuraciones"), self.settings_window.open_settings),
                ("separator", None),
                (self.tr("Salir"), self.quit),
            ], x=0)


    def create_menu_frame(self, options: List[Any], x: int) -> ctk.CTkFrame:
        # Crear el marco del menú con fondo oscuro y borde de sombra para resaltar
        menu_frame = ctk.CTkFrame(self, corner_radius=5, fg_color="gray25", border_color="black", border_width=1)
        menu_frame.place(x=x, y=30)
        
        # Agregar sombra alrededor del menú
        menu_frame.configure(border_width=1, border_color="black")

        # Evitar la propagación del clic en el menú
        menu_frame.bind("<Button-1>", lambda e: "break")

        # Añadir opciones al menú con separación entre elementos
        for option in options:
            if option[0] == "separator":
                separator = ctk.CTkFrame(menu_frame, height=1, fg_color="gray50")
                separator.pack(fill="x", padx=5, pady=5)
                separator.bind("<Button-1>", lambda e: "break")
            elif option[1] is None:
                # Texto sin comando (por ejemplo, título de submenú)
                label = ctk.CTkLabel(menu_frame, text=option[0], anchor="w", fg_color="gray30")
                label.pack(fill="x", padx=5, pady=2)
                label.bind("<Button-1>", lambda e: "break")
            else:
                btn = ctk.CTkButton(
                    menu_frame,
                    text=option[0],
                    fg_color="transparent",
                    hover_color="gray35",
                    anchor="w",
                    text_color="white",
                    command=lambda cmd=option[1]: cmd()
                )
                btn.pack(fill="x", padx=5, pady=2)
                btn.bind("<Button-1>", lambda e: "break")

        return menu_frame

    def close_all_menus(self) -> None:
        for menu_frame in [self.archivo_menu_frame, self.ayuda_menu_frame, self.donaciones_menu_frame]:
            if menu_frame and menu_frame.winfo_exists():
                menu_frame.destroy()
    
    # Queue management methods
    def on_queue_changed(self) -> None:
        """Called when the download queue changes."""
        # Update the queue button badge
        self.update_queue_badge()
    
    def show_queue_manager(self) -> None:
        """Show the download queue manager dialog."""
        from app.dialogs.queue_dialog import QueueDialog
        queue_dialog = QueueDialog(
            self, 
            self.download_queue, 
            self.tr,
            on_process_queue=self.process_queue,
            on_process_all=self.process_queue_all,
            on_pause_all=self.pause_all_queue,
            on_resume_all=self.resume_all_queue,
            on_stop_processing=self.stop_queue_processing
        )
        queue_dialog.focus_set()

    def stop_queue_processing(self) -> None:
        """Stop Process All mode (does not cancel an active download)."""
        self._process_queue_all_active = False

    def pause_all_queue(self) -> None:
        """Pause all pending items (does not pause an active download)."""
        from app.models.download_queue import QueueItemStatus
        self._process_queue_all_active = False
        for item in self.download_queue.get_all():
            if item.status == QueueItemStatus.PENDING:
                self.download_queue.update_status(item.id, QueueItemStatus.PAUSED)

    def resume_all_queue(self) -> None:
        """Resume all paused items back to pending."""
        from app.models.download_queue import QueueItemStatus
        for item in self.download_queue.get_all():
            if item.status == QueueItemStatus.PAUSED:
                self.download_queue.update_status(item.id, QueueItemStatus.PENDING)
    
    def add_to_queue(self) -> None:
        """Add URLs from input to the download queue."""
        # Get URLs from the input panel (supports batch input)
        urls = self.input_panel.get_urls()
        
        if not urls:
            messagebox.showerror(self.tr("Error"), self.tr("Por favor, ingresa al menos una URL."))
            return
            
        if not hasattr(self, 'download_folder') or not self.download_folder:
            messagebox.showerror(self.tr("Error"), self.tr("Por favor, selecciona una carpeta de descarga."))
            return
        
        # Add each URL to the queue
        added_count = 0
        for url in urls:
            url = url.strip()
            if url:
                from app.models.download_queue import QueuePriority
                self.download_queue.add(
                    url=url,
                    download_folder=self.download_folder,
                    priority=QueuePriority.NORMAL
                )
                added_count += 1
        
        # Show success message
        if added_count > 0:
            self.add_log_message_safe(
                self.tr("{count} URL(s) added to queue", count=added_count)
            )
            messagebox.showinfo(
                self.tr("Success"),
                self.tr("{count} URL(s) added to queue. Open Queue Manager to view and process.", count=added_count)
            )
            
            # Clear input after adding to queue
            self.input_panel.url_entry.delete("1.0", "end")
            
            # Update queue button badge if menu bar exists
            self.update_queue_badge()

    def update_queue_badge(self) -> None:
        """Update the queue button to show pending count."""
        stats = self.download_queue.get_stats()
        pending_count = stats['pending'] + stats['downloading']
        
        # Update the queue button text with badge
        if hasattr(self, 'queue_button') and self.queue_button:
            if pending_count > 0:
                self.queue_button.configure(text=f"📋 {self.tr('Queue')} ({pending_count})")
            else:
                self.queue_button.configure(text="📋 " + self.tr("Queue"))
    
    def process_queue(self) -> None:
        """Process pending items from the download queue."""
        # Get the next pending item
        item = self.download_queue.get_next_pending()
        
        if not item:
            messagebox.showinfo(
                self.tr("Queue Empty"),
                self.tr("No pending items in queue to process.")
            )
            # If we were running a batch queue process, stop it
            if getattr(self, "_process_queue_all_active", False):
                self._process_queue_all_active = False
            return
        
        # Update item status to downloading
        from app.models.download_queue import QueueItemStatus
        self.download_queue.update_status(item.id, QueueItemStatus.DOWNLOADING)
        
        # Log the start
        self.add_log_message_safe(
            self.tr("Processing queue item: {url}...", url=item.url[:60])
        )
        
        # Set the download folder for this item
        original_folder = self.download_folder if hasattr(self, 'download_folder') else None
        self.download_folder = item.download_folder
        
        # Store the item ID for status updates
        self._current_queue_item_id = item.id
        
        # Process the URL using existing download logic
        try:
            self._process_single_url(item.url)
            # Note: The actual completion/failure will be handled in the download callbacks
        except Exception as e:
            self.add_log_message_safe(
                self.tr("Error processing queue item: {error}", error=str(e))
            )
            self.download_queue.update_status(
                item.id, 
                QueueItemStatus.FAILED,
                error_message=str(e)
            )
        finally:
            # Restore original folder (or reset if it was None)
            self.download_folder = original_folder

    def process_queue_all(self) -> None:
        """Process all pending queue items sequentially."""
        self._process_queue_all_active = True
        # Kick off first item
        self.process_queue()

    # Image processing
    def create_photoimage(self, path: str, size: Tuple[int, int] = (32, 32)) -> ImageTk.PhotoImage:
        img = Image.open(path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        photoimg = ImageTk.PhotoImage(img)
        return photoimg

    # Folder selection
    
    # Función para cargar y redimensionar imágenes
    def load_and_resize_image(self, path: str, size: Tuple[int, int] = (20, 20)) -> ctk.CTkImage:
        img = Image.open(path)
        return ctk.CTkImage(img, size=size)
    
    # Reemplaza las llamadas a los métodos de progreso con self.progress_manager
    def update_progress(self, downloaded: int, total: int, file_id: Optional[str] = None, file_path: Optional[str] = None, speed: Optional[float] = None, eta: Optional[float] = None, status: Optional[str] = None) -> None:
        self.progress_manager.update_progress(downloaded, total,file_id, file_path,speed, eta, status=status)

        # Best-effort queue item progress (for per-file style downloaders)
        if hasattr(self, '_current_queue_item_id') and self._current_queue_item_id:
            try:
                if total and total > 0:
                    frac = min(max(downloaded / total, 0.0), 1.0)
                    self._throttled_update_queue_item_progress(frac)
            except Exception:
                pass

    def remove_progress_bar(self, file_id: str) -> None:
        self.progress_manager.remove_progress_bar(file_id)

    def update_global_progress(self, completed_files: int, total_files: int) -> None:
        self.progress_manager.update_global_progress(completed_files, total_files)

        # Queue item progress (for multi-file jobs)
        if hasattr(self, '_current_queue_item_id') and self._current_queue_item_id:
            try:
                if total_files and total_files > 0:
                    frac = min(max(completed_files / total_files, 0.0), 1.0)
                    self._throttled_update_queue_item_progress(frac)
            except Exception:
                pass

    def _throttled_update_queue_item_progress(self, progress: float) -> None:
        """Update queue item progress with throttling to avoid excessive disk writes."""
        try:
            now = time.time()
        except Exception:
            return

        if (now - getattr(self, '_queue_progress_last_update', 0.0)) < getattr(self, '_queue_progress_throttle_seconds', 0.25):
            return

        self._queue_progress_last_update = now

        try:
            if hasattr(self, '_current_queue_item_id') and self._current_queue_item_id:
                from app.models.download_queue import QueueItemStatus
                # Keep status as DOWNLOADING while updating progress
                self.download_queue.update_status(
                    self._current_queue_item_id,
                    QueueItemStatus.DOWNLOADING,
                    progress=float(progress)
                )
        except Exception:
            pass

    def toggle_progress_details(self) -> None:
        self.progress_manager.toggle_progress_details()

    def center_progress_details_frame(self) -> None:
        self.progress_manager.center_progress_details_frame()

    # Error logging
    def log_error(self, error_message: str) -> None:
        self.errors.append(error_message)
        self.add_log_message_safe(f"Error: {error_message}")

    def _create_download_controller(self) -> DownloadController:
        """Create and configure a DownloadController instance."""
        return DownloadController(
            download_folder=self.download_folder,
            settings=self.settings,
            max_downloads=self.max_downloads,
            log_callback=self.add_log_message_safe,
            update_progress_callback=self.update_progress,
            update_global_progress_callback=self.update_global_progress,
            enable_widgets_callback=self.enable_widgets,
            export_logs_callback=self.export_logs,
            get_download_images=lambda: self.download_images_check.get(),
            get_download_videos=lambda: self.download_videos_check.get(),
            get_download_compressed=lambda: self.download_compressed_check.get(),
            get_download_documents=lambda: self.download_documents_check.get(),
            tr=self.tr,
            progress_manager=self.progress_manager,
            root=self
        )

    # Download management
    def start_download(self) -> None:
        # Get URLs from the input panel (supports batch input)
        urls = self.input_panel.get_urls()
        
        if not urls:
            messagebox.showerror(self.tr("Error"), self.tr("Por favor, ingresa al menos una URL."))
            return
            
        if not hasattr(self, 'download_folder') or not self.download_folder:
            messagebox.showerror(self.tr("Error"), self.tr("Por favor, selecciona una carpeta de descarga."))
            return
        
        # For batch downloads, process URLs sequentially
        if len(urls) > 1:
            # Check for duplicates
            unique_urls = []
            seen_urls = set()
            duplicates_count = 0
            
            for url in urls:
                normalized_url = url.strip()
                if normalized_url in seen_urls:
                    duplicates_count += 1
                else:
                    seen_urls.add(normalized_url)
                    unique_urls.append(normalized_url)
            
            if duplicates_count > 0:
                self.add_log_message_safe(self.tr(f"Removed {duplicates_count} duplicate URLs from the batch."))
                urls = unique_urls

            self.add_log_message_safe(self.tr(f"Batch download: {len(urls)} unique URLs detected"))
            for i, url in enumerate(urls, 1):
                self.add_log_message_safe(self.tr(f"Processing URL {i}/{len(urls)}: {url[:60]}..."))
                self._process_single_url(url)
        else:
            # Single URL - process normally
            self._process_single_url(urls[0])
    
    def _process_single_url(self, url: str) -> None:
        """Process a single URL using the DownloadController."""
        if not hasattr(self, 'download_folder') or not self.download_folder:
            messagebox.showerror(self.tr("Error"), self.tr("Por favor, selecciona una carpeta de descarga."))
            return

        # Set download start time and reset errors
        self.download_start_time = datetime.datetime.now()
        self.errors = []
        
        # Create controller and process URL
        controller = self._create_download_controller()
        
        download_thread = controller.process_url(
            url,
            on_download_button_callback=lambda state: self.download_button.configure(state=state),
            on_cancel_button_callback=lambda state: self.cancel_button.configure(state=state)
        )
        
        if download_thread is None:
            # Controller couldn't process this URL (invalid or unsupported)
            messagebox.showerror(
                self.tr("Error"),
                self.tr("This URL is not supported. Supported sites include:\n"
                       "- YouTube, Vimeo, Twitter/X, TikTok, Instagram\n"
                       "- Coomer, Kemono, Erome, Bunkr, SimpCity, Jpg5\n"
                       "- 1000+ other sites via yt-dlp")
            )
            return
        
        # Store the active downloader for cancellation support
        self.active_downloader = controller.get_active_downloader()
        
        # Start the download thread
        download_thread.start()

    def extract_user_id(self, url: str) -> Optional[str]:
        self.add_log_message_safe(self.tr("Extrayendo ID del usuario del URL: {url}", url=url))
        match = re.search(r'/user/([^/?]+)', url)
        if match:
            user_id = match.group(1)
            self.add_log_message_safe(self.tr("ID del usuario extraído: {user_id}", user_id=user_id))
            return user_id
        else:
            self.add_log_message_safe(self.tr("No se pudo extraer el ID del usuario."))
            messagebox.showerror(self.tr("Error"), self.tr("No se pudo extraer el ID del usuario."))
            return None

    def extract_post_id(self, url: str) -> Optional[str]:
        match = re.search(r'/post/([^/?]+)', url)
        if match:
            post_id = match.group(1)
            self.add_log_message_safe(self.tr("ID del post extraído: {post_id}", post_id=post_id))
            return post_id
        else:
            self.add_log_message_safe(self.tr("No se pudo extraer el ID del post."))
            messagebox.showerror(self.tr("Error"), self.tr("No se pudo extraer el ID del post."))
            return None

    def cancel_download(self) -> None:
        if self.active_downloader:
            self.active_downloader.request_cancel()
            self.active_downloader = None
            self.clear_progress_bars()
            
            # Update queue item status if cancelling from queue
            if hasattr(self, '_current_queue_item_id') and self._current_queue_item_id:
                from app.models.download_queue import QueueItemStatus
                self.download_queue.update_status(
                    self._current_queue_item_id,
                    QueueItemStatus.CANCELLED
                )
                self._current_queue_item_id = None
        else:
            self.add_log_message_safe(self.tr("No hay una descarga en curso para cancelar."))
        self.enable_widgets()

    def clear_progress_bars(self) -> None:
        for file_id in list(self.progress_bars.keys()):
            self.remove_progress_bar(file_id)

    # Log messages safely
    def add_log_message_safe(self, message: str) -> None:
        # Ensure structures exist
        if not hasattr(self, "errors") or self.errors is None:
            self.errors = []
        
        # Only add ERROR messages to errors list
        if message and ("error" in message.lower() or "failed" in message.lower() or "falló" in message.lower()):
            self.errors.append(message)

        # Try to write to textbox if it exists; otherwise buffer
        try:
            if hasattr(self, "log_textbox") and self.log_textbox:
                self.log_textbox.configure(state="normal")
                self.log_textbox.insert("end", message + "\n")
                self.log_textbox.configure(state="disabled")

                if getattr(self, "autoscroll_logs_var", None) and self.autoscroll_logs_var.get():
                    self.log_textbox.see("end")
            else:
                # textbox doesn't exist yet; buffer the message
                if not hasattr(self, "_log_buffer") or self._log_buffer is None:
                    self._log_buffer = []
                self._log_buffer.append(message)
        except Exception:
            # on any problem, also buffer
            if not hasattr(self, "_log_buffer") or self._log_buffer is None:
                self._log_buffer = []
            self._log_buffer.append(message)


    def limit_log_lines(self) -> None:
        log_lines = self.log_textbox.get("1.0", "end-1c").split("\n")
        if len(log_lines) > MAX_LOG_LINES:
            # Quitamos solo las líneas que sobran
            overflow = len(log_lines) - MAX_LOG_LINES
            self.log_textbox.delete("1.0", f"{overflow}.0")


    # Export logs to a file
    def export_logs(self) -> None:
        log_folder = "resources/config/logs/"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        log_file_path = Path(log_folder) / f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            if self.active_downloader:
                total_files = self.active_downloader.total_files
                completed_files = self.active_downloader.completed_files
                skipped_files = self.active_downloader.skipped_files
                failed_files = self.active_downloader.failed_files
            else:
                total_files = 0
                completed_files = 0
                skipped_files = []
                failed_files = []
            
            # Info general
            total_images = completed_files if self.download_images_check.get() else 0
            total_videos = completed_files if self.download_videos_check.get() else 0
            errors = len(self.errors)
            warnings = len(self.warnings)
            if self.download_start_time:
                duration = datetime.datetime.now() - self.download_start_time
            else:
                duration = "N/A"

            skipped_files_summary = "\n".join(skipped_files)
            failed_files_summary = "\n".join(failed_files)

            summary = (
                f"Total de archivos descargados: {total_files}\n"
                f"Total de imágenes descargadas: {total_images}\n"
                f"Total de videos descargados: {total_videos}\n"
                f"Errores: {errors}\n"
                f"Advertencias: {warnings}\n"
                f"Tiempo total de descarga: {duration}\n\n"
                f"Archivos saltados:\n{skipped_files_summary}\n\n"
                f"Archivos fallidos:\n{failed_files_summary}\n\n"
            )

            with open(log_file_path, 'w', encoding='utf-8') as file:
                # Escribimos el resumen
                file.write(summary)
                # Escribimos TODOS los mensajes (no solo los del textbox)
                file.write("\n--- LOGS COMPLETOS ---\n")
                file.write("\n".join(self.all_logs))

            self.add_log_message_safe(f"Logs exportados exitosamente a {log_file_path}")
        except Exception as e:
            self.add_log_message_safe(f"No se pudo exportar los logs: {e}")


    # Clipboard operations (updated for CTkTextbox)
    def copy_to_clipboard(self) -> None:
        try:
            # CTkTextbox uses tk.SEL tag for selection
            selected_text = self.url_entry.get("sel.first", "sel.last")
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            else:
                self.add_log_message_safe(self.tr("No hay texto seleccionado para copiar."))
        except tk.TclError:
            self.add_log_message_safe(self.tr("No hay texto seleccionado para copiar."))

    def paste_from_clipboard(self) -> None:
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                try:
                    self.url_entry.delete("sel.first", "sel.last")  # Delete selected text if any
                except tk.TclError:
                    pass
                self.url_entry.insert(tk.INSERT, clipboard_text)
            else:
                self.add_log_message_safe(self.tr("No hay texto en el portapapeles para pegar."))
        except tk.TclError as e:
            self.add_log_message_safe(self.tr(f"Error al pegar desde el portapapeles: {e}"))

    def cut_to_clipboard(self) -> None:
        try:
            selected_text = self.url_entry.get("sel.first", "sel.last")
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.url_entry.delete("sel.first", "sel.last")
            else:
                self.add_log_message_safe(self.tr("No hay texto seleccionado para cortar."))
        except tk.TclError:
            self.add_log_message_safe(self.tr("No hay texto seleccionado para cortar."))


    # Show context menu
    def show_context_menu(self, event: Any) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
        self.context_menu.grab_release()

    # Update queue
    def check_update_queue(self) -> None:
        while not self.update_queue.empty():
            task = self.update_queue.get_nowait()
            task()
        self.after(100, self.check_update_queue)

    # Enable widgets
    def enable_widgets(self) -> None:
        self.update_queue.put(lambda: self.download_button.configure(state="normal"))
        self.update_queue.put(lambda: self.cancel_button.configure(state="disabled"))
        
        # Update queue item status if processing from queue
        if hasattr(self, '_current_queue_item_id') and self._current_queue_item_id:
            from app.models.download_queue import QueueItemStatus
            # Check if there were errors
            if self.errors:
                self.download_queue.update_status(
                    self._current_queue_item_id,
                    QueueItemStatus.FAILED,
                    error_message="; ".join(self.errors)
                )
            else:
                self.download_queue.update_status(
                    self._current_queue_item_id,
                    QueueItemStatus.COMPLETED,
                    progress=1.0
                )
            self._current_queue_item_id = None

            # Auto-continue if Process All is active
            if getattr(self, "_process_queue_all_active", False):
                # Schedule next item after UI has re-enabled
                self.after(0, self._continue_queue_all)

    def _continue_queue_all(self) -> None:
        if not getattr(self, "_process_queue_all_active", False):
            return
        # If no more pending items, stop
        item = self.download_queue.get_next_pending()
        if not item:
            self._process_queue_all_active = False
            messagebox.showinfo(
                self.tr("Queue Complete"),
                self.tr("All queued items have been processed.")
            )
            return
        self.process_queue()

    # Save and load download folder
    def save_download_folder(self, folder_path: str) -> None:
        config = {'download_folder': folder_path}
        with open('resources/config/download_path/download_folder.json', 'w') as config_file:
            json.dump(config, config_file)

    def load_download_folder(self) -> str:
        config_path = 'resources/config/download_path/download_folder.json'
        config_dir = Path(config_path).parent
        if not config_dir.exists():
            config_dir.mkdir(parents=True)
        if not Path(config_path).exists():
            with open(config_path, 'w') as config_file:
                json.dump({'download_folder': ''}, config_file)
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                return config.get('download_folder', '')
        except json.JSONDecodeError:
            return ''

    # Update max downloads
    def update_max_downloads(self, max_downloads: int) -> None:
        self.max_downloads = max_downloads
        if hasattr(self, 'general_downloader'):
            self.general_downloader.max_workers = max_downloads
        if hasattr(self, 'erome_downloader'):
            self.erome_downloader.max_workers = max_downloads
        if hasattr(self, 'bunkr_downloader'):
            self.bunkr_downloader.max_workers = max_downloads

    def get_github_stars(self, user: str, repo: str, timeout: float = 2.5) -> int:
        try:
            url = f"https://api.github.com/repos/{user}/{repo}"
            headers = {
                "User-Agent": "CoomerDL",
                "Accept": "application/vnd.github+json",
            }
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            return int(data.get("stargazers_count", 0))
        except Exception:
            # No rompas el arranque si no hay internet
            self.add_log_message_safe(self.tr("Offline mode: GitHub stars could not be retrieved."))
            return 0

    def load_icon(self, icon_path: str, icon_name: str) -> Optional[Image.Image]:
        try:
            img = Image.open(icon_path)
            return img  # Devuelve la imagen de PIL
        except Exception as e:
            self.add_log_message_safe(f"Error al cargar el icono {icon_name}: {e}")
            return None

    # Uso de la función genérica para cargar íconos específicos
    def load_github_icon(self) -> Optional[Image.Image]:
        return self.load_icon("resources/img/iconos/ui/social/github-logo-24.png", "GitHub")

    def load_discord_icon(self) -> Optional[Image.Image]:
        return self.load_icon("resources/img/iconos/ui/social/discord-alt-logo-24.png", "Discord")

    def load_patreon_icon(self) -> Optional[Image.Image]:
        return self.load_icon("resources/img/iconos/ui/social/patreon-logo-24.png", "New Icon")

    def parse_version_string(self, version_str: str) -> Tuple[int, ...]:
      # Removes 'V' prefix and splits by '.'
      try:
          return tuple(int(p) for p in version_str[1:].split('.'))
      except (ValueError, IndexError):
          return (0, 0, 0) # Fallback for invalid format

    def check_for_new_version(self, startup_check: bool = False) -> None:
        repo_owner = "primoscope"
        repo_name = "CoomerDL"
        github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        
        try:
            response = requests.get(github_api_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            latest_release = response.json()
            
            latest_tag = latest_release.get("tag_name")
            latest_url = latest_release.get("html_url")

            if latest_tag and latest_url:
                # Use the global VERSION constant directly
                current_version_parsed = self.parse_version_string(VERSION) 
                latest_version_parsed = self.parse_version_string(latest_tag)

                if latest_version_parsed > current_version_parsed:
                    self.latest_release_url = latest_url
                    # Use functools.partial to ensure 'self' is correctly bound
                    self.after(0, functools.partial(self.show_update_alert, latest_tag))
                    if not startup_check:
                        self.after(0, lambda: messagebox.showinfo(
                            self.tr("Update Available"),
                            self.tr("A new version ({latest_tag}) is available! Please download it from GitHub.", latest_tag=latest_tag)
                        ))
                else:
                    if not startup_check:
                        self.after(0, lambda: messagebox.showinfo(
                            self.tr("No Updates"),
                            self.tr("You are running the latest version.")
                        ))
            else:
                if not startup_check:
                    self.after(0, lambda: messagebox.showwarning(
                        self.tr("Update Check Failed"),
                        self.tr("Could not retrieve latest version information from GitHub.")
                    ))
        except requests.exceptions.RequestException as e:
            if self._is_offline_error(e):
                self.add_log_message_safe(self.tr("Offline mode: could not check for updates."))
                self.after(0, lambda: messagebox.showinfo(
                    self.tr("No Internet connection"),
                    self.tr("We couldn't check for updates. You may not be connected to the Internet right now.\n\nThe app will continue to work in offline mode.")
                ))
            else:
                self.add_log_message_safe(f"Error checking for updates: {e}")
                if not startup_check:
                    self.after(0, lambda: messagebox.showerror(
                        self.tr("Network Error"),
                        self.tr("Could not connect to GitHub to check for updates. Please check your internet connection.")
                    ))
        except Exception as e:
            self.add_log_message_safe(f"An unexpected error occurred during update check: {e}")
            if not startup_check:
                self.after(0, lambda: messagebox.showerror(
                    self.tr("Error"),
                    self.tr("An unexpected error occurred during update check.")
                ))

    def show_update_alert(self, latest_tag: str) -> None:
        self.update_alert_label.configure(text=self.tr("New version ({latest_tag}) available!", latest_tag=latest_tag))
        self.update_alert_frame.pack(side="top", fill="x")
        # Re-pack other elements to ensure they are below the alert
        self.input_panel.pack_forget()
        self.input_panel.pack(fill='x', padx=20, pady=20)
        self.options_panel.pack_forget()
        self.options_panel.pack(pady=10, fill='x', padx=20)
        self.action_panel.pack_forget()
        self.action_panel.pack(pady=10, fill='x', padx=20)
        self.log_panel.pack_forget()
        self.log_panel.pack(pady=(10, 0), padx=20, fill='both', expand=True)
        self.progress_panel.pack_forget()
        self.progress_panel.pack(pady=(0, 10), fill='x', padx=20)

    def open_latest_release(self) -> None:
        if hasattr(self, 'latest_release_url'):
            webbrowser.open(self.latest_release_url)
        else:
            messagebox.showwarning(self.tr("No Release Found"), self.tr("No latest release URL available."))

    def _is_offline_error(self, err: Exception) -> bool:
        s = str(err)
        return (
            isinstance(err, requests.exceptions.ConnectionError)
            or "NameResolutionError" in s
            or "getaddrinfo failed" in s
            or "Failed to establish a new connection" in s
            or "Max retries exceeded" in s
        )
