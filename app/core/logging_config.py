
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_directory / "application.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        handlers=[file_handler, console_handler],
        force=True,
    )
