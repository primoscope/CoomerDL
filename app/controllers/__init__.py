"""
Controllers package - Business logic layer.

This package contains controllers that coordinate between the UI and core
download functionality, keeping the UI layer thin and testable.
"""

from app.controllers.download_controller import DownloadController

__all__ = ['DownloadController']
