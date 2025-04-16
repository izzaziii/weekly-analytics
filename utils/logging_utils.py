"""
Logging utilities for the weekly-analytics project.

This module provides a configurable logging system with context information
that can be used throughout the application.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union

# Configure the base logger
logger = logging.getLogger("weekly_analytics")

# Default log format with timestamp, level, module, and message
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logging(
    log_level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None,
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (default: INFO)
        log_format: Log format string (default: includes timestamp, level, module, message)
        log_file: Optional path to log file. If provided, logs will be written to this file.
    """
    # Convert string log level to int if needed
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure the logger
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log file is specified
    if log_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Name for the logger (default: None, which returns the root logger)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"weekly_analytics.{name}")
    return logger


class ContextLogger:
    """
    Logger class that adds context information to log messages.

    This class wraps a standard logger but adds context information to each message,
    making it easier to trace operations across the application.
    """

    def __init__(self, name: str = None, context: Dict[str, Any] = None):
        """
        Initialize a context logger.

        Args:
            name: Logger name
            context: Initial context dictionary
        """
        self.logger = get_logger(name)
        self.context = context or {}

    def add_context(self, **kwargs) -> None:
        """
        Add key-value pairs to the context.

        Args:
            **kwargs: Key-value pairs to add to the context
        """
        self.context.update(kwargs)

    def _format_message(self, msg: str) -> str:
        """Format message with context information."""
        if not self.context:
            return msg

        context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{msg} [Context: {context_str}]"

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message with context."""
        self.logger.debug(self._format_message(msg), *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message with context."""
        self.logger.info(self._format_message(msg), *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message with context."""
        self.logger.warning(self._format_message(msg), *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message with context."""
        self.logger.error(self._format_message(msg), *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message with context."""
        self.logger.critical(self._format_message(msg), *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception message with context."""
        self.logger.exception(self._format_message(msg), *args, **kwargs)


# Initialize logging with default configuration
setup_logging()
