"""
Domain Rate Limiter - Per-domain concurrency and request rate limiting.

Provides thread-safe rate limiting for HTTP requests across domains.
"""
from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from typing import Dict, Optional
from urllib.parse import urlparse

from downloader.policies import DomainPolicy, DEFAULT_DOMAIN_POLICY


class DomainRecord:
    """Internal record for tracking domain state."""
    
    def __init__(self, max_concurrency: int):
        self.semaphore = threading.Semaphore(max_concurrency)
        self.last_request_time: float = 0.0
        self.lock = threading.Lock()


class DomainLimiter:
    """
    Thread-safe per-domain rate limiter.
    
    Enforces:
    - Maximum concurrent requests per domain
    - Minimum interval between requests to the same domain
    
    Usage:
        limiter = DomainLimiter()
        
        # Context manager (recommended)
        with limiter.limit("example.com"):
            response = requests.get("https://example.com/api")
        
        # Manual acquire/release
        limiter.acquire("example.com")
        try:
            response = requests.get("https://example.com/api")
        finally:
            limiter.release("example.com")
    """
    
    def __init__(self, policy: Optional[DomainPolicy] = None):
        """
        Initialize the domain limiter.
        
        Args:
            policy: Domain policy configuration. Uses defaults if None.
        """
        self.policy = policy or DEFAULT_DOMAIN_POLICY
        self._domains: Dict[str, DomainRecord] = {}
        self._global_lock = threading.Lock()
    
    def _get_or_create_record(self, domain: str) -> DomainRecord:
        """Get or create a domain record."""
        with self._global_lock:
            if domain not in self._domains:
                self._domains[domain] = DomainRecord(
                    self.policy.per_domain_max_concurrency
                )
            return self._domains[domain]
    
    def acquire(self, domain: str) -> None:
        """
        Acquire permission to make a request to domain.
        
        Blocks until:
        - Concurrency slot is available
        - Minimum interval has elapsed since last request
        
        Args:
            domain: Domain name (e.g., "example.com").
        """
        record = self._get_or_create_record(domain)
        
        # Acquire concurrency slot
        record.semaphore.acquire()
        
        # Enforce minimum interval
        with record.lock:
            now = time.time()
            elapsed = now - record.last_request_time
            wait_time = self.policy.min_interval_seconds - elapsed
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            record.last_request_time = time.time()
    
    def release(self, domain: str) -> None:
        """
        Release a domain slot after request completes.
        
        Args:
            domain: Domain name.
        """
        record = self._get_or_create_record(domain)
        record.semaphore.release()
    
    @contextmanager
    def limit(self, domain: str):
        """
        Context manager for rate-limited requests.
        
        Args:
            domain: Domain name.
            
        Yields:
            None - just manages acquire/release.
        """
        self.acquire(domain)
        try:
            yield
        finally:
            self.release(domain)
    
    @contextmanager
    def limit_url(self, url: str):
        """
        Context manager for rate-limited requests using URL.
        
        Extracts domain from URL automatically.
        
        Args:
            url: Full URL.
            
        Yields:
            None - just manages acquire/release.
        """
        domain = extract_domain(url)
        with self.limit(domain):
            yield
    
    def get_active_count(self, domain: str) -> int:
        """
        Get number of active requests to a domain.
        
        Args:
            domain: Domain name.
            
        Returns:
            Number of currently active requests (approximate).
        """
        record = self._get_or_create_record(domain)
        # Semaphore doesn't expose count directly, so we track indirectly
        max_conc = self.policy.per_domain_max_concurrency
        # Try to acquire without blocking to see available slots
        acquired = record.semaphore.acquire(blocking=False)
        if acquired:
            record.semaphore.release()
            return max_conc - 1  # At most max-1 active if we got one
        return max_conc  # All slots taken


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL.
        
    Returns:
        Domain name (e.g., "example.com").
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        # Remove www prefix for consistency
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain or 'unknown'
    except Exception:
        return 'unknown'


# Global shared limiter instance (optional usage)
_global_limiter: Optional[DomainLimiter] = None
_limiter_lock = threading.Lock()


def get_global_limiter(policy: Optional[DomainPolicy] = None) -> DomainLimiter:
    """
    Get or create the global domain limiter.
    
    Args:
        policy: Optional policy for initialization.
        
    Returns:
        Shared DomainLimiter instance.
    """
    global _global_limiter
    with _limiter_lock:
        if _global_limiter is None:
            _global_limiter = DomainLimiter(policy)
        return _global_limiter
