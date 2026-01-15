"""
Download Policies - Shared retry, backoff, and concurrency policies.

Provides centralized configuration for:
- Retry behavior with exponential backoff and jitter
- Per-domain concurrency limits and minimum intervals
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Set, Tuple, Type
from requests.exceptions import (
    ConnectionError, Timeout, ChunkedEncodingError,
    ContentDecodingError
)


@dataclass
class RetryPolicy:
    """
    Configuration for retry behavior with exponential backoff.
    
    Attributes:
        max_attempts: Maximum number of retry attempts (includes initial try).
        base_delay: Initial delay in seconds before first retry.
        max_delay: Maximum delay cap in seconds.
        jitter: Random variation factor (0.2 = +/- 20%).
        retryable_statuses: HTTP status codes that should trigger retry.
        retryable_exceptions: Exception types that should trigger retry.
    """
    max_attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: float = 0.2
    retryable_statuses: Set[int] = field(
        default_factory=lambda: {429, 500, 502, 503, 504}
    )
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (
            ConnectionError,
            Timeout,
            ChunkedEncodingError,
            ContentDecodingError,
        )
    )
    
    def is_retryable_status(self, status_code: int) -> bool:
        """Check if HTTP status code should trigger retry."""
        return status_code in self.retryable_statuses
    
    def is_retryable_exception(self, exc: Exception) -> bool:
        """Check if exception should trigger retry."""
        return isinstance(exc, self.retryable_exceptions)


@dataclass
class DomainPolicy:
    """
    Configuration for per-domain concurrency and rate limiting.
    
    Attributes:
        per_domain_max_concurrency: Maximum concurrent requests per domain.
        min_interval_seconds: Minimum time between requests to same domain.
    """
    per_domain_max_concurrency: int = 2
    min_interval_seconds: float = 1.0


# Default policies
DEFAULT_RETRY_POLICY = RetryPolicy()
DEFAULT_DOMAIN_POLICY = DomainPolicy()


def compute_backoff(attempt: int, policy: RetryPolicy) -> float:
    """
    Compute backoff delay for a given retry attempt.
    
    Uses exponential backoff with optional jitter:
    delay = min(base_delay * 2^attempt, max_delay) * (1 +/- jitter)
    
    Args:
        attempt: Retry attempt number (0-indexed, 0 = first retry).
        policy: RetryPolicy configuration.
        
    Returns:
        Delay in seconds before next retry.
    """
    # Exponential backoff: base * 2^attempt
    delay = policy.base_delay * (2 ** attempt)
    
    # Cap at max_delay
    delay = min(delay, policy.max_delay)
    
    # Apply jitter if configured
    if policy.jitter > 0:
        jitter_range = delay * policy.jitter
        delay = delay + random.uniform(-jitter_range, jitter_range)
        # Ensure delay doesn't go negative or exceed max
        delay = max(0.1, min(delay, policy.max_delay))
    
    return delay


def compute_backoff_sequence(policy: RetryPolicy) -> list:
    """
    Compute the full sequence of backoff delays for a policy.
    
    Useful for testing and documentation.
    
    Args:
        policy: RetryPolicy configuration.
        
    Returns:
        List of delays for each attempt.
    """
    # Use jitter=0 for deterministic sequence
    temp_policy = RetryPolicy(
        max_attempts=policy.max_attempts,
        base_delay=policy.base_delay,
        max_delay=policy.max_delay,
        jitter=0
    )
    return [
        compute_backoff(i, temp_policy)
        for i in range(policy.max_attempts - 1)
    ]
