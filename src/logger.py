"""
Structured logging configuration for the pipeline.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str = "weather_pipeline") -> logging.Logger:
    """Create and configure the application logger."""
    _logger = logging.getLogger(name)

    if _logger.handlers:
        return _logger

    _logger.setLevel(logging.INFO)

    # ── Console handler (stdout — captured by Docker) ────────
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_fmt)
    _logger.addHandler(console_handler)

    # ── File handler (optional, for local runs) ──────────────
    try:
        import os
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(
            f"logs/pipeline_{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(console_fmt)
        _logger.addHandler(file_handler)
    except OSError:
        _logger.warning("Could not create log file — logging to stdout only")

    return _logger


# Module-level logger instance
logger = setup_logger()
