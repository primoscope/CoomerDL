"""
Universal Scraper Settings Tab for Settings Window.
"""
from __future__ import annotations

import customtkinter as ctk


class ScraperSettingsTab:
    """UI component for universal scraper settings."""
    
    def __init__(self, parent_frame, translate, settings):
        """
        Initialize the scraper settings tab.
        
        Args:
            parent_frame: Parent CTk frame.
            translate: Translation function.
            settings: Settings dictionary.
        """
        self.parent = parent_frame
        self.translate = translate
        self.settings = settings
        
        # Initialize scraper settings if not present
        if 'scraper' not in self.settings:
            self.settings['scraper'] = {
                'enabled': True,
                'auto_detect_media': True,
                'follow_redirects': True,
                'max_redirects': 5,
                'download_videos': True,
                'download_images': True,
                'download_audio': True,
                'download_archives': False,
                'quality_preference': 'best',
                'min_file_size_mb': 0,
                'max_file_size_mb': 0,
            }
        
        self.render()
    
    def render(self):
        """Render the scraper settings UI."""
        # Main container
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.parent,
            text=self.translate("Universal Scraper Settings"),
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Description
        desc = ctk.CTkLabel(
            self.parent,
            text=self.translate("Configure intelligent media detection for any webpage"),
            font=("Helvetica", 10),
            text_color="gray"
        )
        desc.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Enable smart detection
        self.enable_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('enabled', True)
        )
        enable_check = ctk.CTkCheckBox(
            self.parent,
            text=self.translate("Enable Smart Detection"),
            variable=self.enable_var
        )
        enable_check.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
        
        # Auto-detect media type
        self.auto_detect_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('auto_detect_media', True)
        )
        auto_detect_check = ctk.CTkCheckBox(
            self.parent,
            text=self.translate("Auto-detect media type from URL"),
            variable=self.auto_detect_var
        )
        auto_detect_check.grid(row=3, column=0, sticky="w", padx=20, pady=5)
        
        # Follow redirects
        redirect_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        redirect_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        
        self.follow_redirects_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('follow_redirects', True)
        )
        redirect_check = ctk.CTkCheckBox(
            redirect_frame,
            text=self.translate("Follow redirects (max:"),
            variable=self.follow_redirects_var
        )
        redirect_check.pack(side="left")
        
        self.max_redirects_var = ctk.IntVar(
            value=self.settings['scraper'].get('max_redirects', 5)
        )
        redirect_entry = ctk.CTkEntry(redirect_frame, textvariable=self.max_redirects_var, width=50)
        redirect_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(redirect_frame, text=")").pack(side="left")
        
        # Media types section
        media_frame = ctk.CTkFrame(self.parent)
        media_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(15, 10))
        media_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            media_frame,
            text=self.translate("Media Types to Download:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        types_frame = ctk.CTkFrame(media_frame, fg_color="transparent")
        types_frame.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        
        self.download_videos_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('download_videos', True)
        )
        ctk.CTkCheckBox(
            types_frame,
            text=self.translate("Videos"),
            variable=self.download_videos_var
        ).pack(side="left", padx=(0, 15))
        
        self.download_images_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('download_images', True)
        )
        ctk.CTkCheckBox(
            types_frame,
            text=self.translate("Images"),
            variable=self.download_images_var
        ).pack(side="left", padx=(0, 15))
        
        self.download_audio_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('download_audio', True)
        )
        ctk.CTkCheckBox(
            types_frame,
            text=self.translate("Audio"),
            variable=self.download_audio_var
        ).pack(side="left", padx=(0, 15))
        
        self.download_archives_var = ctk.BooleanVar(
            value=self.settings['scraper'].get('download_archives', False)
        )
        ctk.CTkCheckBox(
            types_frame,
            text=self.translate("Archives"),
            variable=self.download_archives_var
        ).pack(side="left")
        
        # Quality preference
        quality_frame = ctk.CTkFrame(self.parent)
        quality_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 10))
        quality_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            quality_frame,
            text=self.translate("Quality Preference:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        self.quality_var = ctk.StringVar(
            value=self.settings['scraper'].get('quality_preference', 'best')
        )
        
        ctk.CTkRadioButton(
            quality_frame,
            text=self.translate("Best Available"),
            variable=self.quality_var,
            value="best"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        
        ctk.CTkRadioButton(
            quality_frame,
            text=self.translate("Medium (720p/1080p cap)"),
            variable=self.quality_var,
            value="medium"
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        
        ctk.CTkRadioButton(
            quality_frame,
            text=self.translate("Low (480p cap, data saver)"),
            variable=self.quality_var,
            value="low"
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        
        ctk.CTkRadioButton(
            quality_frame,
            text=self.translate("Audio Only"),
            variable=self.quality_var,
            value="audio"
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=15, pady=(2, 15))
        
        # File size limits
        size_frame = ctk.CTkFrame(self.parent)
        size_frame.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 10))
        size_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(
            size_frame,
            text=self.translate("File Size Limits:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            size_frame,
            text=self.translate("Min:"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        
        self.min_size_var = ctk.IntVar(
            value=self.settings['scraper'].get('min_file_size_mb', 0)
        )
        ctk.CTkEntry(
            size_frame,
            textvariable=self.min_size_var,
            width=80
        ).grid(row=1, column=1, sticky="w", padx=5, pady=(0, 15))
        
        ctk.CTkLabel(
            size_frame,
            text=self.translate("MB    Max:"),
            anchor="w"
        ).grid(row=1, column=2, sticky="w", padx=15, pady=(0, 15))
        
        self.max_size_var = ctk.IntVar(
            value=self.settings['scraper'].get('max_file_size_mb', 0)
        )
        ctk.CTkEntry(
            size_frame,
            textvariable=self.max_size_var,
            width=80
        ).grid(row=1, column=3, sticky="w", padx=5, pady=(0, 15))
        
        ctk.CTkLabel(
            size_frame,
            text=self.translate("MB (0 = no limit)"),
            anchor="w"
        ).grid(row=1, column=4, sticky="w", padx=5, pady=(0, 15))
    
    def get_settings(self):
        """Get the current settings values."""
        return {
            'enabled': self.enable_var.get(),
            'auto_detect_media': self.auto_detect_var.get(),
            'follow_redirects': self.follow_redirects_var.get(),
            'max_redirects': self.max_redirects_var.get(),
            'download_videos': self.download_videos_var.get(),
            'download_images': self.download_images_var.get(),
            'download_audio': self.download_audio_var.get(),
            'download_archives': self.download_archives_var.get(),
            'quality_preference': self.quality_var.get(),
            'min_file_size_mb': self.min_size_var.get(),
            'max_file_size_mb': self.max_size_var.get(),
        }
