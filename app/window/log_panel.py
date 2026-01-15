"""
Log Panel Component Module

Handles log textbox with auto-scroll functionality.
Extracted from ui.py to improve modularity.
"""
from __future__ import annotations

import tkinter as tk
import customtkinter as ctk
from typing import Callable


class LogPanel(ctk.CTkTextbox):
    """
    Log panel component with scrollable text display.
    """
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        autoscroll_var: tk.BooleanVar,
        width: int = 590,
        height: int = 200,
    ):
        """
        Initialize the log panel.
        
        Args:
            parent: Parent widget
            tr: Translation function
            autoscroll_var: Variable controlling auto-scroll behavior
            width: Width of the textbox
            height: Height of the textbox
        """
        super().__init__(parent, width=width, height=height)
        
        self.tr = tr
        self.autoscroll_var = autoscroll_var
        
        # Set initial state to disabled (read-only)
        self.configure(state="disabled")
    
    def add_log(self, message: str):
        """
        Add a log message to the textbox.
        
        Args:
            message: The log message to add
        """
        self.configure(state="normal")
        self.insert("end", message + "\n")
        self.configure(state="disabled")
        
        # Auto-scroll if enabled
        if self.autoscroll_var.get():
            self.see("end")
    
    def clear_logs(self):
        """Clear all log messages."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
    
    def get_logs(self) -> str:
        """Get all log text."""
        return self.get("1.0", "end-1c")
    
    def export_logs(self, filepath: str):
        """
        Export logs to a file.
        
        Args:
            filepath: Path to save the log file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.get_logs())
        except Exception as e:
            raise Exception(f"Failed to export logs: {e}")
