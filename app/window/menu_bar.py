"""
Menu Bar Component Module

This module provides a reusable menu bar component that can be integrated into the main UI.
Extracted from ui.py to improve modularity and maintainability.
"""
from __future__ import annotations

import customtkinter as ctk
import webbrowser
from typing import Callable, Optional
from PIL import Image


class MenuBar(ctk.CTkFrame):
    """
    Custom menu bar component with File, About, Patreons menus and social icons.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        on_settings: Optional[Callable] = None,
        on_about: Optional[Callable] = None,
        on_donors: Optional[Callable] = None,
        on_queue: Optional[Callable] = None,
        github_stars: int = 0,
        github_icon: Optional[Image.Image] = None,
        discord_icon: Optional[Image.Image] = None,
        patreon_icon: Optional[Image.Image] = None,
    ):
        """
        Initialize the menu bar.
        
        Args:
            parent: Parent widget
            tr: Translation function
            on_settings: Callback for settings button
            on_about: Callback for about button
            on_donors: Callback for donors/patreons button
            on_queue: Callback for queue manager button
            github_stars: Number of GitHub stars to display
            github_icon: GitHub icon image
            discord_icon: Discord icon image
            patreon_icon: Patreon icon image
        """
        super().__init__(parent, fg_color="gray20", height=40)
        
        self.tr = tr
        self.on_settings = on_settings
        self.on_about = on_about
        self.on_donors = on_donors
        self.on_queue = on_queue
        self.github_stars = github_stars
        self.github_icon = github_icon
        self.discord_icon = discord_icon
        self.patreon_icon = patreon_icon
        
        # Menu state
        self.archivo_menu_frame = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all menu bar widgets."""
        # File button (Archivo)
        archivo_button = ctk.CTkButton(
            self,
            text=self.tr("Archivo"),
            width=80,
            fg_color="transparent",
            hover_color="gray25",
            command=self.toggle_archivo_menu
        )
        archivo_button.pack(side="left", padx=2)
        archivo_button.bind("<Button-1>", lambda e: "break")
        
        # About button
        if self.on_about:
            about_button = ctk.CTkButton(
                self,
                text=self.tr("About"),
                width=80,
                fg_color="transparent",
                hover_color="gray25",
                command=self.on_about
            )
            about_button.pack(side="left", padx=2)
            about_button.bind("<Button-1>", lambda e: "break")
        
        # Patreons/Donors button
        if self.on_donors:
            donors_button = ctk.CTkButton(
                self,
                text=self.tr("Patreons"),
                width=80,
                fg_color="transparent",
                hover_color="gray25",
                command=self.on_donors
            )
            donors_button.pack(side="left", padx=2)
            donors_button.bind("<Button-1>", lambda e: "break")
        
        # Queue button (NEW)
        if self.on_queue:
            self.queue_button = ctk.CTkButton(
                self,
                text="📋 " + self.tr("Queue"),
                width=80,
                fg_color="transparent",
                hover_color="gray25",
                command=self.on_queue
            )
            self.queue_button.pack(side="left", padx=2)
            self.queue_button.bind("<Button-1>", lambda e: "break")
        else:
            self.queue_button = None
        
        # Right side icons
        self._create_social_icons()
    
    def _create_social_icons(self):
        """Create GitHub, Discord, and Patreon icon links."""
        def on_enter(event, frame):
            frame.configure(fg_color="gray25")
        
        def on_leave(event, frame):
            frame.configure(fg_color="transparent")
        
        # GitHub icon with stars
        if self.github_icon:
            resized_github_icon = self.github_icon.resize((16, 16), Image.Resampling.LANCZOS)
            resized_github_icon = ctk.CTkImage(resized_github_icon)
            github_frame = ctk.CTkFrame(self, cursor="hand2", fg_color="transparent", corner_radius=5)
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
    
    def toggle_archivo_menu(self):
        """Toggle the File (Archivo) dropdown menu."""
        if self.archivo_menu_frame and self.archivo_menu_frame.winfo_exists():
            self.archivo_menu_frame.destroy()
            self.archivo_menu_frame = None
        else:
            self.show_archivo_menu()
    
    def show_archivo_menu(self):
        """Show the File (Archivo) dropdown menu."""
        # Create dropdown menu frame
        self.archivo_menu_frame = ctk.CTkFrame(
            self.master,  # Attach to parent window
            fg_color="gray20",
            corner_radius=5,
            border_width=1,
            border_color="gray30"
        )
        self.archivo_menu_frame.place(x=10, y=50)  # Position below button
        
        # Settings option
        if self.on_settings:
            settings_btn = ctk.CTkButton(
                self.archivo_menu_frame,
                text=self.tr("Settings"),
                fg_color="transparent",
                hover_color="gray25",
                anchor="w",
                command=lambda: (self.on_settings(), self.archivo_menu_frame.destroy())
            )
            settings_btn.pack(fill="x", padx=5, pady=2)
        
        # Exit option
        exit_btn = ctk.CTkButton(
            self.archivo_menu_frame,
            text=self.tr("Exit"),
            fg_color="transparent",
            hover_color="gray25",
            anchor="w",
            command=self.master.quit
        )
        exit_btn.pack(fill="x", padx=5, pady=2)
        
        # Click outside to close
        def close_menu(event):
            if self.archivo_menu_frame and event.widget != self.archivo_menu_frame:
                try:
                    if not any(w == event.widget for w in self.archivo_menu_frame.winfo_children()):
                        self.archivo_menu_frame.destroy()
                        self.archivo_menu_frame = None
                except:
                    pass
        
        self.master.bind("<Button-1>", close_menu, add="+")
    
    def update_github_stars(self, stars: int):
        """Update the GitHub stars count display."""
        self.github_stars = stars
        # Recreate widgets to update display
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
    
    def update_queue_badge(self, count: int):
        """Update the queue button to show pending item count."""
        if self.queue_button:
            if count > 0:
                self.queue_button.configure(text=f"📋 {self.tr('Queue')} ({count})")
            else:
                self.queue_button.configure(text="📋 " + self.tr("Queue"))
