"""
A module for managing system configs of fukurou contents.
"""
from .baseconfig import BaseConfig, BaseSubConfig
from .exceptions import NewConfigInterrupt
from .service import ConfigService, Config, add_config, get_config
