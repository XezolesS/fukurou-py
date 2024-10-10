from __future__ import annotations
from dataclasses import dataclass, field

from fukurou.configs import Config

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "fmt_console": {
            "format": "[%(asctime)s | %(name)s %(levelname)s] %(message)s",
            "datefmt": "%m-%d-%Y %H:%M:%S"
        },
        "fmt_file": {
            "format": "[%(asctime)s | %(name)s %(levelname)s] %(message)s",
            "datefmt": "%m-%d-%Y %H:%M:%S"
        }
    },
    "filters": {

    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "fmt_console",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "fmt_file",
            "level": "INFO",
            "filename": "logs/fukurou.log",
            "when": "midnight",
            "backupCount": 30
        }
    },
    "loggers": {
        "fukurou": {
            "level": "INFO",
            "propagate": False,
            "handlers": [ "console", "file" ]
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [ "console", "file" ]
    }
}

@dataclass
class BotConfig(Config, filename='fukurou.json'):
    token: str = 'INSERT_TOKEN'
    extensions: list[str] = field(default_factory=list)
    logging: dict = field(default_factory=lambda: DEFAULT_LOGGING_CONFIG)
