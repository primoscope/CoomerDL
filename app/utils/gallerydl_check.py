"""
Gallery-dl Check Utility - Verify gallery-dl availability.

Provides functions to check if gallery-dl is installed and accessible.
"""
from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def check_gallerydl() -> Tuple[bool, str]:
    """
    Check if gallery-dl is available and get version.
    
    Returns:
        Tuple of (is_available, version_or_error_message)
    """
    try:
        import gallery_dl
        version = getattr(gallery_dl, '__version__', 'unknown')
        logger.debug(f"gallery-dl found, version: {version}")
        return (True, version)
    except ImportError as e:
        error_msg = "gallery-dl is not installed. Install with: pip install gallery-dl"
        logger.warning(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Error checking gallery-dl: {e}"
        logger.error(error_msg)
        return (False, error_msg)


def get_gallerydl_version() -> str:
    """
    Get the installed gallery-dl version string.
    
    Returns:
        Version string, or empty string if not available.
    """
    ok, result = check_gallerydl()
    return result if ok else ""


def is_gallerydl_available() -> bool:
    """
    Quick check if gallery-dl is available.
    
    Returns:
        True if gallery-dl is installed, False otherwise.
    """
    ok, _ = check_gallerydl()
    return ok
