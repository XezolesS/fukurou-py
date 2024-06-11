"""
A module for managing system configs of fukurou contents.
"""
from .interfaces import BaseConfig, BaseSubConfig
from .exceptions import NewConfigInterrupt
from .service import ConfigService, Config, add_config, get_config

__all__ = [
    'BaseConfig',
    'BaseSubConfig',
    'Config',
    'add_config',
    'get_config'    
]
