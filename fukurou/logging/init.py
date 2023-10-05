import logging
import sys

from fukurou.configs import configs
from .loghanlder import LogHandler

def init_logger() -> logging.Logger:
    """
        Initialize a Logger
    """
    logger = logging.getLogger('Fukurou')
    logger.setLevel(logging.INFO)

    log_config = configs.get_config('logging')
    formatter = logging.Formatter(log_config.log_format, log_config.log_time)

    stream_handler = init_stream(fmt=formatter)
    file_handler = init_file(fmt=formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

def init_stream(fmt: logging.Formatter) -> logging.StreamHandler:
    """
        Initialize a StreamHandler for a logger.
    """
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt=fmt)

    return stream_handler

def init_file(fmt: logging.Formatter) -> logging.FileHandler:
    """
        Initialize a FileHandler for a logger.
    """
    log_handler = LogHandler()
    file = log_handler.create_next()

    file_handler = logging.FileHandler(filename=file, encoding='utf-8', mode='w')
    file_handler.setFormatter(fmt=fmt)

    return file_handler
