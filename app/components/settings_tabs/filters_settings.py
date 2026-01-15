"""
Advanced Filters Settings Tab for Settings Window.
"""
from __future__ import annotations

import customtkinter as ctk
from tkinter import StringVar, IntVar, BooleanVar
from datetime import datetime


class FiltersSettingsTab:
    """UI component for advanced filtering settings."""
    
    def __init__(self, parent_frame, translate, settings):
        """
        Initialize the filters settings tab.
        
        Args:
            parent_frame: Parent CTk frame.
            translate: Translation function.
            settings: Settings dictionary.
        """
        self.parent = parent_frame
        self.translate = translate
        self.settings = settings
        
        # Initialize filters settings if not present
        if 'filters' not in self.settings:
            self.settings['filters'] = {
                'min_file_size_mb': 0,
                'max_file_size_mb': 0,
                'date_from': '',
                'date_to': '',
                'exclude_webm': False,
                'exclude_gif': False,
                'exclude_webp': False,
                'exclude_zip': False,
                'exclude_rar': False,
            }
        
        self.render()
    
    def render(self):
        """Render the filters settings UI."""
        # Main container
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.parent,
            text=self.translate("Advanced Filters"),
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # File size filters section
        size_frame = ctk.CTkFrame(self.parent)
        size_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        size_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            size_frame,
            text=self.translate("File Size Filters:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        # Minimum file size
        ctk.CTkLabel(
            size_frame,
            text=self.translate("Minimum file size (MB, 0=no limit):"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.min_size_var = ctk.IntVar(
            value=self.settings['filters'].get('min_file_size_mb', 0)
        )
        ctk.CTkEntry(
            size_frame,
            textvariable=self.min_size_var,
            width=80
        ).grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        # Maximum file size
        ctk.CTkLabel(
            size_frame,
            text=self.translate("Maximum file size (MB, 0=no limit):"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(5, 15))
        
        self.max_size_var = ctk.IntVar(
            value=self.settings['filters'].get('max_file_size_mb', 0)
        )
        ctk.CTkEntry(
            size_frame,
            textvariable=self.max_size_var,
            width=80
        ).grid(row=2, column=1, sticky="w", padx=15, pady=(5, 15))
        
        # Date range filters section
        date_frame = ctk.CTkFrame(self.parent)
        date_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        date_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            date_frame,
            text=self.translate("Date Range Filters:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        # Date from
        ctk.CTkLabel(
            date_frame,
            text=self.translate("From date (YYYY-MM-DD, empty=no limit):"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.date_from_var = ctk.StringVar(
            value=self.settings['filters'].get('date_from', '')
        )
        ctk.CTkEntry(
            date_frame,
            textvariable=self.date_from_var,
            placeholder_text="2024-01-01"
        ).grid(row=1, column=1, sticky="ew", padx=15, pady=5)
        
        # Date to
        ctk.CTkLabel(
            date_frame,
            text=self.translate("To date (YYYY-MM-DD, empty=no limit):"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(5, 15))
        
        self.date_to_var = ctk.StringVar(
            value=self.settings['filters'].get('date_to', '')
        )
        ctk.CTkEntry(
            date_frame,
            textvariable=self.date_to_var,
            placeholder_text="2024-12-31"
        ).grid(row=2, column=1, sticky="ew", padx=15, pady=(5, 15))
        
        # File type exclusions section
        exclude_frame = ctk.CTkFrame(self.parent)
        exclude_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        exclude_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            exclude_frame,
            text=self.translate("Exclude File Types:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Create checkboxes for common file types
        self.exclude_webm_var = ctk.BooleanVar(
            value=self.settings['filters'].get('exclude_webm', False)
        )
        ctk.CTkCheckBox(
            exclude_frame,
            text=self.translate("Exclude WEBM videos"),
            variable=self.exclude_webm_var
        ).grid(row=1, column=0, sticky="w", padx=15, pady=2)
        
        self.exclude_gif_var = ctk.BooleanVar(
            value=self.settings['filters'].get('exclude_gif', False)
        )
        ctk.CTkCheckBox(
            exclude_frame,
            text=self.translate("Exclude GIF images"),
            variable=self.exclude_gif_var
        ).grid(row=2, column=0, sticky="w", padx=15, pady=2)
        
        self.exclude_webp_var = ctk.BooleanVar(
            value=self.settings['filters'].get('exclude_webp', False)
        )
        ctk.CTkCheckBox(
            exclude_frame,
            text=self.translate("Exclude WEBP images"),
            variable=self.exclude_webp_var
        ).grid(row=3, column=0, sticky="w", padx=15, pady=2)
        
        self.exclude_zip_var = ctk.BooleanVar(
            value=self.settings['filters'].get('exclude_zip', False)
        )
        ctk.CTkCheckBox(
            exclude_frame,
            text=self.translate("Exclude ZIP archives"),
            variable=self.exclude_zip_var
        ).grid(row=4, column=0, sticky="w", padx=15, pady=2)
        
        self.exclude_rar_var = ctk.BooleanVar(
            value=self.settings['filters'].get('exclude_rar', False)
        )
        ctk.CTkCheckBox(
            exclude_frame,
            text=self.translate("Exclude RAR archives"),
            variable=self.exclude_rar_var
        ).grid(row=5, column=0, sticky="w", padx=15, pady=(2, 15))
        
        # Info label
        info_label = ctk.CTkLabel(
            self.parent,
            text=self.translate("Note: Filters apply to future downloads. Files matching the criteria will be skipped."),
            font=("Helvetica", 10),
            text_color="gray",
            wraplength=700,
            anchor="w",
            justify="left"
        )
        info_label.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 20))
    
    def _validate_date(self, date_str: str) -> str:
        """
        Validate and return date string in ISO format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Valid ISO date string or empty string
        """
        if not date_str:
            return ''
        
        try:
            from datetime import datetime
            # Try to parse the date
            dt = datetime.fromisoformat(date_str)
            # Return in ISO format
            return dt.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            # Invalid date, return empty string
            return ''
    
    def get_settings(self):
        """Get the current settings values with date validation."""
        return {
            'min_file_size_mb': self.min_size_var.get(),
            'max_file_size_mb': self.max_size_var.get(),
            'date_from': self._validate_date(self.date_from_var.get().strip()),
            'date_to': self._validate_date(self.date_to_var.get().strip()),
            'exclude_webm': self.exclude_webm_var.get(),
            'exclude_gif': self.exclude_gif_var.get(),
            'exclude_webp': self.exclude_webp_var.get(),
            'exclude_zip': self.exclude_zip_var.get(),
            'exclude_rar': self.exclude_rar_var.get(),
        }
