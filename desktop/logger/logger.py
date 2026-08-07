"""
logger.py
Logger terpusat untuk seluruh aplikasi desktop. Menulis ke console + file
harian di desktop/logger/logs/. Dipakai oleh service/repository/controller
lewat get_logger(__name__).
"""
import logging
import sys
from logging.handlers import RotatingFileHandler

from desktop.config.settings import LOG_DIR, LOG_LEVEL

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_configured_loggers = set()


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if name in _configured_loggers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.DEBUG))
    logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        file_handler = RotatingFileHandler(
            LOG_DIR / "gsmartclass.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # Jika direktori log tidak bisa ditulis (mis. read-only fs), cukup log ke console.
        pass

    _configured_loggers.add(name)
    return logger
