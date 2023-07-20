from . import BaseConfig
from .confighandler import ConfigHandler

config_handler = ConfigHandler()

def get_config_handler() -> ConfigHandler:
    return config_handler

def add_config(config: BaseConfig):
    config_handler.add_config(config)
