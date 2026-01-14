import subprocess
import threading
import os
import re
import shlex
from typing import Callable, Optional
from app.utils.ffmpeg_check import get_ffmpeg_path, check_ffprobe

class MediaConverter:
    def __init__(self):
        self.ffmpeg = get_ffmpeg_path()
        self.ffprobe = "ffprobe" if check_ffprobe() else None
        self.stop_event = threading.Event()
        self.current_process = None

    def get_duration(self, file_path):
        if not self.ffprobe:
            return 0
        try:
            cmd = [
                self.ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return float(res.stdout.strip())
        except (ValueError, subprocess.TimeoutExpired, subprocess.SubprocessError):
            return 0

    def convert(self, input_path, output_path, options, progress_callback: Optional[Callable[[float, str], None]] = None):
        """
        Convert media file.
        options: dict with 'format', 'args' (string of extra args)
        """
        if not self.ffmpeg:
            raise FileNotFoundError("FFmpeg not found")

        self.stop_event.clear()

        # Build Command
        cmd = [self.ffmpeg, "-y", "-i", input_path]

        # Add options - use shlex.split() for safe argument parsing
        # This prevents command injection by properly handling shell metacharacters
        if options.get('args'):
            try:
                extra_args = shlex.split(options['args'])
                cmd.extend(extra_args)
            except ValueError as e:
                raise ValueError(f"Invalid FFmpeg arguments: {e}")

        cmd.append(output_path)

        duration = self.get_duration(input_path)

        # Run
        try:
            # We need to capture stderr to parse progress
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace' # Handle potential encoding issues
            )

            # Read stderr for progress
            while True:
                if self.stop_event.is_set():
                    self.current_process.kill()
                    break

                line = self.current_process.stderr.readline()
                if not line and self.current_process.poll() is not None:
                    break

                if line:
                    # Parse time=HH:MM:SS.fraction
                    # Examples: time=00:00:05.1, time=00:00:05.12, time=00:00:05.123456
                    match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d+)", line)
                    if match and duration and duration > 0:
                        h, m, s = map(int, match.group(1, 2, 3))
                        frac_str = match.group(4)
                        frac_sec = int(frac_str) / (10 ** len(frac_str))
                        current_sec = h * 3600 + m * 60 + s + frac_sec
                        # Use defensive effective duration to avoid division by zero
                        effective_duration = max(duration, 1.0)
                        percent = min(0.99, current_sec / effective_duration)
                        if progress_callback:
                            progress_callback(percent, f"Converting... {int(percent*100)}%")

            if self.current_process.returncode == 0:
                if progress_callback: progress_callback(1.0, "Conversion Complete")
                return True
            else:
                if not self.stop_event.is_set():
                    # Capture stderr for better error reporting
                    stderr_output = self.current_process.stderr.read() if self.current_process.stderr else ""
                    error_msg = f"FFmpeg conversion failed with return code {self.current_process.returncode}"
                    if stderr_output:
                        error_msg += f". Error: {stderr_output[:200]}"
                    raise Exception(error_msg)
                return False

        except Exception as e:
            if progress_callback: progress_callback(0, f"Error: {e}")
            raise e
        finally:
            self.current_process = None

    def cancel(self):
        self.stop_event.set()
        if self.current_process:
            try:
                self.current_process.terminate()
            except OSError:
                # Process may have already exited; nothing to do.
                pass
