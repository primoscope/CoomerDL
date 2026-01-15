"""
Logging Manager for CoomerDL.

Provides centralized logging with file rotation, console output, and real-time callbacks.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
from logging.handlers import RotatingFileHandler
import threading


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    @property
    def logging_level(self):
        """Convert to Python logging level."""
        return getattr(logging, self.value)


@dataclass
class LogConfig:
    """Configuration for the logging system."""
    enabled: bool = False
    file_logging: bool = True
    console_logging: bool = False
    log_directory: str = "logs"
    log_level: LogLevel = LogLevel.INFO
    max_file_size_mb: int = 10
    max_files: int = 5
    include_timestamp: bool = True
    include_source: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'enabled': self.enabled,
            'file_logging': self.file_logging,
            'console_logging': self.console_logging,
            'log_directory': self.log_directory,
            'log_level': self.log_level.value,
            'max_file_size_mb': self.max_file_size_mb,
            'max_files': self.max_files,
            'include_timestamp': self.include_timestamp,
            'include_source': self.include_source,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'LogConfig':
        """Create from dictionary."""
        config = LogConfig()
        config.enabled = data.get('enabled', False)
        config.file_logging = data.get('file_logging', True)
        config.console_logging = data.get('console_logging', False)
        config.log_directory = data.get('log_directory', 'logs')
        
        # Parse log level
        level_str = data.get('log_level', 'INFO')
        try:
            config.log_level = LogLevel(level_str)
        except ValueError:
            config.log_level = LogLevel.INFO
        
        config.max_file_size_mb = data.get('max_file_size_mb', 10)
        config.max_files = data.get('max_files', 5)
        config.include_timestamp = data.get('include_timestamp', True)
        config.include_source = data.get('include_source', True)
        
        return config


class LoggingManager:
    """
    Centralized logging manager for CoomerDL.
    
    Features:
    - File logging with rotation
    - Real-time terminal/console output
    - Log level filtering
    - Structured log format
    - Thread-safe operations
    """
    
    def __init__(self, config: Optional[LogConfig] = None):
        """
        Initialize the logging manager.
        
        Args:
            config: Logging configuration. If None, uses default config.
        """
        self.config = config or LogConfig()
        self._log_callbacks: List[Callable[[str, LogLevel], None]] = []
        self._recent_logs: List[str] = []
        self._max_recent_logs = 1000
        self._lock = threading.Lock()
        self._logger = None
        
        if self.config.enabled:
            self._setup_logging()
    
    def _setup_logging(self):
        """Set up the Python logging infrastructure."""
        # Create logger
        self._logger = logging.getLogger('CoomerDL')
        self._logger.setLevel(self.config.log_level.logging_level)
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Build format string
        fmt_parts = []
        if self.config.include_timestamp:
            fmt_parts.append('%(asctime)s')
        fmt_parts.append('[%(levelname)s]')
        if self.config.include_source:
            fmt_parts.append('%(name)s')
        fmt_parts.append('%(message)s')
        
        log_format = ' - '.join(fmt_parts)
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        
        # File logging
        if self.config.file_logging:
            # Create log directory
            os.makedirs(self.config.log_directory, exist_ok=True)
            
            # Create rotating file handler
            log_file = os.path.join(
                self.config.log_directory,
                f"coomerdl_{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                backupCount=self.config.max_files
            )
            file_handler.setLevel(self.config.log_level.logging_level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        
        # Console logging
        if self.config.console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config.log_level.logging_level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        # Add custom handler for callbacks and recent logs
        callback_handler = CallbackHandler(self._on_log_record)
        callback_handler.setLevel(self.config.log_level.logging_level)
        callback_handler.setFormatter(formatter)
        self._logger.addHandler(callback_handler)
    
    def _on_log_record(self, record: logging.LogRecord, formatted_message: str):
        """Handle log record for callbacks and recent logs storage."""
        with self._lock:
            # Store in recent logs
            self._recent_logs.append(formatted_message)
            if len(self._recent_logs) > self._max_recent_logs:
                self._recent_logs.pop(0)
            
            # Notify callbacks
            try:
                level = LogLevel(record.levelname)
            except ValueError:
                level = LogLevel.INFO
            
            for callback in self._log_callbacks:
                try:
                    callback(formatted_message, level)
                except Exception as e:
                    # Avoid infinite loops - don't log callback errors
                    print(f"Error in log callback: {e}")
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO, source: Optional[str] = None):
        """
        Log a message with optional source context.
        
        Args:
            message: The message to log.
            level: Log level.
            source: Optional source/module identifier.
        """
        if not self.config.enabled or self._logger is None:
            return
        
        # Get appropriate logger
        if source:
            logger = logging.getLogger(f'CoomerDL.{source}')
        else:
            logger = self._logger
        
        # Log at appropriate level
        logger.log(level.logging_level, message)
    
    def debug(self, message: str, source: Optional[str] = None):
        """Log a debug message."""
        self.log(message, LogLevel.DEBUG, source)
    
    def info(self, message: str, source: Optional[str] = None):
        """Log an info message."""
        self.log(message, LogLevel.INFO, source)
    
    def warning(self, message: str, source: Optional[str] = None):
        """Log a warning message."""
        self.log(message, LogLevel.WARNING, source)
    
    def error(self, message: str, source: Optional[str] = None):
        """Log an error message."""
        self.log(message, LogLevel.ERROR, source)
    
    def critical(self, message: str, source: Optional[str] = None):
        """Log a critical message."""
        self.log(message, LogLevel.CRITICAL, source)
    
    def add_callback(self, callback: Callable[[str, LogLevel], None]):
        """
        Add a callback for real-time log updates.
        
        The callback will be called with (formatted_message, log_level) for each log entry.
        
        Args:
            callback: Function to call with (message: str, level: LogLevel).
        """
        with self._lock:
            if callback not in self._log_callbacks:
                self._log_callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, LogLevel], None]):
        """
        Remove a callback.
        
        Args:
            callback: The callback to remove.
        """
        with self._lock:
            if callback in self._log_callbacks:
                self._log_callbacks.remove(callback)
    
    def get_recent_logs(self, count: int = 100) -> List[str]:
        """
        Get recent log entries.
        
        Args:
            count: Maximum number of recent logs to return.
        
        Returns:
            List of formatted log messages.
        """
        with self._lock:
            return self._recent_logs[-count:].copy()
    
    def export_logs(self, filepath: str):
        """
        Export all recent logs to a file.
        
        Args:
            filepath: Path to save the log file.
        """
        with self._lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                for log_line in self._recent_logs:
                    f.write(log_line + '\n')
    
    def clear_recent_logs(self):
        """Clear the recent logs buffer."""
        with self._lock:
            self._recent_logs.clear()
    
    def update_config(self, config: LogConfig):
        """
        Update the logging configuration.
        
        This will recreate the logging infrastructure with new settings.
        
        Args:
            config: New logging configuration.
        """
        self.config = config
        if self.config.enabled:
            self._setup_logging()
        else:
            if self._logger:
                self._logger.handlers.clear()
                self._logger = None


class CallbackHandler(logging.Handler):
    """Custom logging handler that calls a callback with each log record."""
    
    def __init__(self, callback: Callable[[logging.LogRecord, str], None]):
        """
        Initialize the handler.
        
        Args:
            callback: Function to call with (record, formatted_message).
        """
        super().__init__()
        self.callback = callback
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record."""
        try:
            formatted_message = self.format(record)
            self.callback(record, formatted_message)
        except Exception:
            self.handleError(record)


# Global logging manager instance
_global_logger: Optional[LoggingManager] = None


def get_logger() -> LoggingManager:
    """
    Get the global logging manager instance.
    
    Returns:
        The global LoggingManager instance.
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = LoggingManager()
    return _global_logger


def initialize_logger(config: LogConfig):
    """
    Initialize the global logging manager with configuration.
    
    Args:
        config: Logging configuration.
    """
    global _global_logger
    _global_logger = LoggingManager(config)
