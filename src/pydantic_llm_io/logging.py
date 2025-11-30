"""Logging configuration and utilities."""

import logging
import sys

from .config import LoggingConfig


def setup_logger(
    name: str,
    config: LoggingConfig,
) -> logging.Logger:
    """Set up a custom logger.

    Args:
        name: Logger name
        config: Logging configuration

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(config.get_logging_level())

    # Clear existing handlers to prevent duplicates
    logger.handlers.clear()

    # Formatter configuration
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler configuration (console output)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger (create if necessary).

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Logging helper class with context information."""

    def __init__(self, logger: logging.Logger, context: dict) -> None:
        """Initialize.

        Args:
            logger: Logger instance
            context: Context information
        """
        self.logger = logger
        self.context = context

    def debug(self, message: str) -> None:
        """Log at DEBUG level."""
        self.logger.debug(f"{message} | context: {self.context}")

    def info(self, message: str) -> None:
        """Log at INFO level."""
        self.logger.info(f"{message} | context: {self.context}")

    def warning(self, message: str) -> None:
        """Log at WARNING level."""
        self.logger.warning(f"{message} | context: {self.context}")

    def error(self, message: str) -> None:
        """Log at ERROR level."""
        self.logger.error(f"{message} | context: {self.context}")
