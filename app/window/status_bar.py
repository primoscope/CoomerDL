"""
Status Bar Component Module

Handles ETA and download speed display in the footer.
Extracted from ui.py to improve modularity.
"""
from __future__ import annotations

import customtkinter as ctk
from typing import Callable


class StatusBar(ctk.CTkFrame):
    """
    Status bar component displaying ETA and download speed.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        height: int = 30,
    ):
        """
        Initialize the status bar.
        
        Args:
            parent: Parent widget
            tr: Translation function
            height: Height of the status bar
        """
        super().__init__(parent, height=height, corner_radius=0)
        
        self.tr = tr
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all status bar widgets."""
        # ETA label
        self.footer_eta_label = ctk.CTkLabel(
            self,
            text="ETA: N/A",
            font=("Arial", 11)
        )
        self.footer_eta_label.pack(side="left", padx=20)
        
        # Speed label
        self.footer_speed_label = ctk.CTkLabel(
            self,
            text="Speed: 0 KB/s",
            font=("Arial", 11)
        )
        self.footer_speed_label.pack(side="right", padx=20)
    
    def set_eta(self, eta_text: str):
        """
        Set the ETA text.
        
        Args:
            eta_text: ETA text to display (e.g., "ETA: 5m 30s")
        """
        self.footer_eta_label.configure(text=eta_text)
    
    def set_speed(self, speed_text: str):
        """
        Set the speed text.
        
        Args:
            speed_text: Speed text to display (e.g., "Speed: 1.2 MB/s")
        """
        self.footer_speed_label.configure(text=speed_text)
    
    def update_stats(self, speed: float = None, eta: int = None):
        """
        Update status bar with speed and ETA.
        
        Args:
            speed: Download speed in bytes per second
            eta: Estimated time remaining in seconds
        """
        if speed is not None:
            if speed >= 1024 * 1024:
                speed_text = f"Speed: {speed / (1024 * 1024):.2f} MB/s"
            elif speed >= 1024:
                speed_text = f"Speed: {speed / 1024:.2f} KB/s"
            else:
                speed_text = f"Speed: {speed:.2f} B/s"
            self.set_speed(speed_text)
        
        if eta is not None:
            if eta > 0:
                hours = eta // 3600
                minutes = (eta % 3600) // 60
                seconds = eta % 60
                if hours > 0:
                    eta_text = f"ETA: {hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    eta_text = f"ETA: {minutes}m {seconds}s"
                else:
                    eta_text = f"ETA: {seconds}s"
            else:
                eta_text = "ETA: N/A"
            self.set_eta(eta_text)
    
    def reset(self):
        """Reset status bar to default values."""
        self.set_eta("ETA: N/A")
        self.set_speed("Speed: 0 KB/s")
