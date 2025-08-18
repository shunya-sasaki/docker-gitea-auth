"""Custom logger module."""

import logging
from logging import Formatter
from logging import Logger
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal


class CustomLogger(Logger):
    """Custom logger class that has refined format.

    Args:
        name (str): Name of the logger.
        stream_level (Literal["debug", "info", "warning", "error"]):
            Logging level for the stream handler.
        file_level (Literal["debug", "info", "warning", "error"]):
            Logging level for the file handler.
        log_filename (str): Path to the log file.
        fmt_style (Literal["default", "detailed"]):
            Format style for log messages.
        max_mb (int): Maximum size of the log file in MB before rotation.
        backup_count (int): Number of backup files to keep.
    """

    def __init__(
        self,
        name,
        stream_level: Literal["debug", "info", "warning", "error"],
        file_level: Literal["debug", "info", "warning", "error"],
        log_filename: str,
        fmt_style: Literal["default", "detailed"] = "default",
        max_mb: int = 10,
        backup_count: int = 5,
    ):
        """Initialize the custom logger."""
        super().__init__(name=name)
        match fmt_style:
            case "default":
                fmt: str = "%(levelname)s: " + "[%(asctime)s]" + " %(message)s"
                date_fmt = r"%Y-%m-%d %H:%M:%S"
            case "detailed":
                fmt = (
                    "[%(asctime)s.%(msecs)03d] %(levelname)-8s "
                    + "%(filename)-12s:L %(lineno)-3d"
                    + ": %(message)s"
                )
                date_fmt = r"%Y-%m-%d %H:%M:%S"
        formatter = Formatter(fmt=fmt, datefmt=date_fmt)
        color_formatter = ColorFormatter(fmt=fmt, datefmt=date_fmt)
        stream_handler = StreamHandler()
        stream_handler.setFormatter(color_formatter)
        stream_handler.setLevel(stream_level)
        self.addHandler(stream_handler)
        if log_filename is not None:
            log_filepath = Path(log_filename)
            log_filepath.parent.mkdir(parents=True, exist_ok=True)
            max_bytes = max_mb * 1024 * 1024  # 10 MB
            file_handler = RotatingFileHandler(
                log_filepath,
                maxBytes=max_bytes,
                backupCount=backup_count,
                delay=True,
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(file_level)
            self.addHandler(file_handler)

    @staticmethod
    def _get_package_name():
        current_filepath = Path(__file__)
        parents = list(current_filepath.parents)
        package_name = current_filepath.name.replace(".py", "")
        for parent in parents:
            if (parent_name := parent.name) not in ["src", "site-packages"]:
                package_name = parent_name + "." + package_name
            else:
                return package_name
        raise RuntimeError(
            "Failed to determine package name. "
            + " The package directory should be located in the "
            + "`src` or `site-packages` directory."
        )

    @staticmethod
    def create_config(
        log_filename: str = "log/app.log",
        max_mb: int = 100,
        backup_count: int = 5,
    ) -> dict:
        """Create a configuration dictionary for the logger."""
        package_name = CustomLogger._get_package_name()
        dict_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "()": f"{package_name}.ColorFormatter",
                    "format": "%(levelname)s: "
                    + "[%(asctime)s]"
                    + "%(message)s",
                    "datefmt": r"%Y-%m-%d %H:%M:%S",
                },
                "detail": {
                    "()": f"{package_name}.ColorFormatter",
                    "format": "[%(asctime)s.%(msecs)03d]: %(levelname)-8s"
                    + "%(filename)-16s:L %(lineno)-3d"
                    + ": %(message)s",
                    "datefmt": r"%Y-%m-%d %H:%M:%S",
                },
                "defaultNoColor": {
                    "format": "%(levelname)s: "
                    + "[%(asctime)s]"
                    + "%(message)s",
                    "datefmt": r"%Y-%m-%d %H:%M:%S",
                },
                "detailNoColor": {
                    "format": "[%(asctime)s.%(msecs)03d]: %(levelname)-8s"
                    + "%(filename)-16s:L %(lineno)-3d"
                    + ": %(message)s",
                    "datefmt": r"%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "defaultNoColor",
                    "filename": log_filename,
                    "maxBytes": max_mb * 1024**2,
                    "backupCount": backup_count,
                    "delay": True,
                },
                "streamDetail": {
                    "class": "logging.StreamHandler",
                    "formatter": "detail",
                },
                "fileDetail": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "detailNoColor",
                    "filename": log_filename,
                    "maxBytes": max_mb * 1024**2,
                    "backupCount": backup_count,
                    "delay": True,
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["streamDetail", "fileDetail"],
                "propagate": False,
            },
            "loggers": {
                "detail": {
                    "level": "DEBUG",
                    "handlers": ["streamDetail", "fileDetail"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["streamDetail", "fileDetail"],
                    "propagate": False,
                },
            },
        }
        return dict_config


class ColorFormatter(Formatter):
    """Custom formatter for colored log messages."""

    RESET = "\x1b[0m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"
    LEVEL_CORLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color."""
        original_level = record.levelname
        color = self.LEVEL_CORLORS.get(record.levelno, self.RESET)
        algined_levelname = f"{record.levelname:<8}"
        record.levelname = f"{color}{algined_levelname}{self.RESET}"
        formatted_message = super().format(record)
        record.levelname = original_level  # Restore original level name
        return formatted_message
