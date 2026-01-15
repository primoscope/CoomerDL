"""
Bandwidth throttling for download operations.
"""
from __future__ import annotations

import time
import threading
from typing import Optional


class BandwidthThrottle:
    """
    Controls download bandwidth by limiting bytes per second.
    Thread-safe implementation using locks.
    """
    
    def __init__(self, max_bytes_per_second: int = 0):
        """
        Initialize bandwidth throttle.
        
        Args:
            max_bytes_per_second: Maximum bytes per second (0 = unlimited)
        """
        self.max_bytes_per_second = max_bytes_per_second
        self._lock = threading.Lock()
        self._last_time = time.time()
        self._bytes_sent = 0
    
    def set_limit(self, max_bytes_per_second: int) -> None:
        """
        Update the bandwidth limit.
        
        Args:
            max_bytes_per_second: Maximum bytes per second (0 = unlimited)
        """
        with self._lock:
            self.max_bytes_per_second = max_bytes_per_second
            # Reset counters when limit changes
            self._last_time = time.time()
            self._bytes_sent = 0
    
    def throttle(self, bytes_count: int) -> None:
        """
        Throttle by sleeping if necessary to maintain bandwidth limit.
        
        Args:
            bytes_count: Number of bytes that were just transferred
        """
        if self.max_bytes_per_second <= 0:
            # No limit, return immediately
            return
        
        with self._lock:
            current_time = time.time()
            self._bytes_sent += bytes_count
            
            # Calculate expected time for these bytes
            expected_time = self._bytes_sent / self.max_bytes_per_second
            
            # Calculate actual elapsed time
            elapsed_time = current_time - self._last_time
            
            # If we're going too fast, sleep
            if elapsed_time < expected_time:
                sleep_time = expected_time - elapsed_time
                time.sleep(sleep_time)
            
            # Reset counters every second to prevent drift
            if current_time - self._last_time >= 1.0:
                self._last_time = current_time
                self._bytes_sent = 0
    
    def is_unlimited(self) -> bool:
        """Check if throttling is disabled."""
        return self.max_bytes_per_second <= 0
    
    def get_limit_kbps(self) -> float:
        """Get current limit in KB/s."""
        if self.max_bytes_per_second <= 0:
            return 0.0
        return self.max_bytes_per_second / 1024.0
    
    def get_limit_mbps(self) -> float:
        """Get current limit in MB/s."""
        if self.max_bytes_per_second <= 0:
            return 0.0
        return self.max_bytes_per_second / (1024.0 * 1024.0)
