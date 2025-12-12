"""Structured logging configuration using structlog."""

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Optional logger name for context

    Returns:
        Configured structlog logger
    """
    logger = structlog.get_logger(name)
    return logger
