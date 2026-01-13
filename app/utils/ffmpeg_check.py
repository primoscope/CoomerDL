"""
FFmpeg Check Utility - Verify FFmpeg availability.

Provides functions to check if FFmpeg is installed and accessible.
"""
import shutil
import subprocess
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is available in the system PATH.

    Returns:
        True if FFmpeg is found and executable, False otherwise.
    """
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        logger.debug(f"FFmpeg found at: {ffmpeg_path}")
        return True

    logger.warning(
        "FFmpeg not found in system PATH. "
        "Some video merging and conversion features will be unavailable. "
        "Please install FFmpeg: https://ffmpeg.org/download.html"
    )
    return False


def get_ffmpeg_path() -> Optional[str]:
    """
    Get the path to the FFmpeg executable.

    Returns:
        Path to FFmpeg executable, or None if not found.
    """
    return shutil.which('ffmpeg')


def get_ffmpeg_version() -> Optional[str]:
    """
    Get the installed FFmpeg version string.

    Returns:
        Version string, or None if FFmpeg is not available.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return None

    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # First line typically contains version info
            first_line = result.stdout.split('\n')[0]
            return first_line
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return None


def check_ffmpeg_capabilities() -> Tuple[bool, bool, bool]:
    """
    Check FFmpeg capabilities for common operations.

    Returns:
        Tuple of (can_merge_video_audio, can_convert_to_mp4, can_embed_metadata)
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return (False, False, False)

    try:
        # Check for common encoders/capabilities
        result = subprocess.run(
            [ffmpeg_path, '-encoders'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            output = result.stdout
            # Check for video codec support (aac for audio, h264/libx264 for video)
            can_merge = 'aac' in output or 'libfdk_aac' in output
            can_convert = 'libx264' in output or 'h264' in output
            can_embed_metadata = True  # FFmpeg generally supports metadata
            return (can_merge, can_convert, can_embed_metadata)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return (False, False, False)


def check_ffprobe() -> bool:
    """
    Check if FFprobe is available (comes with FFmpeg).

    Returns:
        True if FFprobe is found, False otherwise.
    """
    return shutil.which('ffprobe') is not None
