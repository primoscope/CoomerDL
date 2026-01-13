"""
Logging Settings Tab for Settings Window.
"""
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox


class LoggingSettingsTab:
    """UI component for logging settings."""
    
    def __init__(self, parent_frame, translate, settings):
        """
        Initialize the logging settings tab.
        
        Args:
            parent_frame: Parent CTk frame.
            translate: Translation function.
            settings: Settings dictionary.
        """
        self.parent = parent_frame
        self.translate = translate
        self.settings = settings
        
        # Initialize logging settings if not present
        if 'logging' not in self.settings:
            self.settings['logging'] = {
                'enabled': False,
                'file_logging': True,
                'console_logging': False,
                'log_directory': 'logs',
                'log_level': 'INFO',
                'max_file_size_mb': 10,
                'max_files': 5,
                'include_timestamp': True,
                'include_source': True,
            }
        
        self.render()
    
    def render(self):
        """Render the logging settings UI."""
        # Main container
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.parent,
            text=self.translate("Logging Settings"),
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Enable logging checkbox
        self.enable_logging_var = ctk.BooleanVar(
            value=self.settings['logging'].get('enabled', False)
        )
        enable_check = ctk.CTkCheckBox(
            self.parent,
            text=self.translate("Enable Logging"),
            variable=self.enable_logging_var,
            command=self._on_enable_changed
        )
        enable_check.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.parent)
        settings_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        settings_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Log level
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("Log Level:"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.log_level_var = ctk.StringVar(
            value=self.settings['logging'].get('log_level', 'INFO')
        )
        log_level_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.log_level_var
        )
        log_level_menu.grid(row=row, column=1, sticky="ew", padx=15, pady=(15, 5))
        row += 1
        
        # File logging
        self.file_logging_var = ctk.BooleanVar(
            value=self.settings['logging'].get('file_logging', True)
        )
        file_logging_check = ctk.CTkCheckBox(
            settings_frame,
            text=self.translate("Write logs to file"),
            variable=self.file_logging_var
        )
        file_logging_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=5)
        row += 1
        
        # Log directory
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("Directory:"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=15, pady=5)
        
        dir_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dir_frame.grid(row=row, column=1, sticky="ew", padx=15, pady=5)
        dir_frame.grid_columnconfigure(0, weight=1)
        
        self.log_dir_var = ctk.StringVar(
            value=self.settings['logging'].get('log_directory', 'logs')
        )
        log_dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.log_dir_var)
        log_dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        browse_btn = ctk.CTkButton(
            dir_frame,
            text=self.translate("Browse..."),
            width=80,
            command=self._browse_directory
        )
        browse_btn.grid(row=0, column=1)
        row += 1
        
        # Max file size
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("Max file size (MB):"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=15, pady=5)
        
        self.max_size_var = ctk.IntVar(
            value=self.settings['logging'].get('max_file_size_mb', 10)
        )
        max_size_entry = ctk.CTkEntry(settings_frame, textvariable=self.max_size_var, width=100)
        max_size_entry.grid(row=row, column=1, sticky="w", padx=15, pady=5)
        row += 1
        
        # Keep last N files
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("Keep last:"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=15, pady=5)
        
        self.max_files_var = ctk.IntVar(
            value=self.settings['logging'].get('max_files', 5)
        )
        max_files_entry = ctk.CTkEntry(settings_frame, textvariable=self.max_files_var, width=100)
        max_files_entry.grid(row=row, column=1, sticky="w", padx=15, pady=5)
        
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("files"),
            anchor="w"
        ).grid(row=row, column=1, sticky="w", padx=(120, 15), pady=5)
        row += 1
        
        # Log format options
        ctk.CTkLabel(
            settings_frame,
            text=self.translate("Log Format:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 5))
        row += 1
        
        self.include_timestamp_var = ctk.BooleanVar(
            value=self.settings['logging'].get('include_timestamp', True)
        )
        timestamp_check = ctk.CTkCheckBox(
            settings_frame,
            text=self.translate("Include timestamp"),
            variable=self.include_timestamp_var
        )
        timestamp_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        row += 1
        
        self.include_source_var = ctk.BooleanVar(
            value=self.settings['logging'].get('include_source', True)
        )
        source_check = ctk.CTkCheckBox(
            settings_frame,
            text=self.translate("Include source/module"),
            variable=self.include_source_var
        )
        source_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(2, 15))
        row += 1
        
        # Action buttons
        button_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=15)
        
        view_logs_btn = ctk.CTkButton(
            button_frame,
            text=self.translate("View Logs"),
            command=self._view_logs
        )
        view_logs_btn.pack(side="left", padx=(0, 10))
        
        export_logs_btn = ctk.CTkButton(
            button_frame,
            text=self.translate("Export Logs"),
            command=self._export_logs
        )
        export_logs_btn.pack(side="left", padx=(0, 10))
        
        clear_logs_btn = ctk.CTkButton(
            button_frame,
            text=self.translate("Clear Logs"),
            command=self._clear_logs
        )
        clear_logs_btn.pack(side="left")
    
    def _on_enable_changed(self):
        """Handle enable logging checkbox change."""
        # Could enable/disable other controls here
        pass
    
    def _browse_directory(self):
        """Browse for log directory."""
        directory = filedialog.askdirectory(
            title=self.translate("Select Log Directory"),
            initialdir=self.log_dir_var.get()
        )
        if directory:
            self.log_dir_var.set(directory)
    
    def _view_logs(self):
        """Open logs directory."""
        log_dir = self.log_dir_var.get()
        if os.path.exists(log_dir):
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == 'Windows':
                    os.startfile(log_dir)
                elif system == 'Darwin':  # macOS
                    subprocess.run(['open', log_dir])
                else:  # Linux
                    subprocess.run(['xdg-open', log_dir])
            except Exception as e:
                messagebox.showerror(
                    self.translate("Error"),
                    self.translate(f"Could not open logs directory: {e}")
                )
        else:
            messagebox.showinfo(
                self.translate("Info"),
                self.translate("No logs directory found. Enable logging to create logs.")
            )
    
    def _export_logs(self):
        """Export logs to a file."""
        try:
            from app.utils.logging_manager import get_logger
            
            logger = get_logger()
            if not logger.config.enabled:
                messagebox.showinfo(
                    self.translate("Info"),
                    self.translate("Logging is not enabled.")
                )
                return
            
            filepath = filedialog.asksaveasfilename(
                title=self.translate("Export Logs"),
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filepath:
                logger.export_logs(filepath)
                messagebox.showinfo(
                    self.translate("Success"),
                    self.translate(f"Logs exported to:\n{filepath}")
                )
        except Exception as e:
            messagebox.showerror(
                self.translate("Error"),
                self.translate(f"Could not export logs: {e}")
            )
    
    def _clear_logs(self):
        """Clear recent logs."""
        if messagebox.askyesno(
            self.translate("Confirm"),
            self.translate("Clear all recent logs from memory?")
        ):
            try:
                from app.utils.logging_manager import get_logger
                
                logger = get_logger()
                logger.clear_recent_logs()
                
                messagebox.showinfo(
                    self.translate("Success"),
                    self.translate("Recent logs cleared.")
                )
            except Exception as e:
                messagebox.showerror(
                    self.translate("Error"),
                    self.translate(f"Could not clear logs: {e}")
                )
    
    def get_settings(self):
        """Get the current settings values."""
        return {
            'enabled': self.enable_logging_var.get(),
            'file_logging': self.file_logging_var.get(),
            'console_logging': False,  # Not exposed in UI yet
            'log_directory': self.log_dir_var.get(),
            'log_level': self.log_level_var.get(),
            'max_file_size_mb': self.max_size_var.get(),
            'max_files': self.max_files_var.get(),
            'include_timestamp': self.include_timestamp_var.get(),
            'include_source': self.include_source_var.get(),
        }
