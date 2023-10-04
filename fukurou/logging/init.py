import logging
import sys

from . import data

formatter = logging.Formatter(data.LOG_FORMAT)

def init_logger() -> logging.Logger:
    """
        Initialize a Logger
    """
    logger = logging.getLogger('Fukurou')
    logger.setLevel(logging.INFO)

    stream_handler = init_stream()
    file_handler = init_file()

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

def init_stream() -> logging.StreamHandler:
    """
        Initialize a StreamHandler for a logger.
    """
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    return stream_handler

def init_file() -> logging.FileHandler:
    """
        Initialize a FileHandler for a logger.
    """
    file_handler = logging.FileHandler(filename=data.FILE_NAME, encoding='utf-8', mode='w')
    file_handler.setFormatter(formatter)

    return file_handler
