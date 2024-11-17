import os
import logging
import logging.config


log_dir = "logs"
log_file = os.path.join(log_dir, "bot.log")

os.makedirs(log_dir, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s "
                      "(module: %(module)s, func: %(funcName)s, line: %(lineno)d)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "detailed",
            "encoding": "utf8",
        },
    },
    "loggers": {
        "bot": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("bot")

__all__ = ["logger"]
