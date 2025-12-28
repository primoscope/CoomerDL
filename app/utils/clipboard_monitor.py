import threading
import time
import pyperclip
from typing import Callable, Optional
import logging

class ClipboardMonitor:
    def __init__(self, callback: Callable[[str], None], interval: float = 1.0):
        self.callback = callback
        self.interval = interval
        self.running = False
        self.last_content = ""
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self):
        if self.running:
            return

        self.running = True
        self._stop_event.clear()

        # Initialize last content to current clipboard so we don't trigger on startup
        try:
            self.last_content = pyperclip.paste()
        except:
            self.last_content = ""

        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _monitor_loop(self):
        while self.running and not self._stop_event.is_set():
            try:
                content = pyperclip.paste()
                if content != self.last_content:
                    self.last_content = content
                    if content and content.strip():
                        # Only trigger callback if content looks like a URL
                        if content.startswith("http://") or content.startswith("https://"):
                            self.callback(content)
            except Exception as e:
                logging.error(f"Clipboard monitor error: {e}")

            time.sleep(self.interval)
