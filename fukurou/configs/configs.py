from . import BaseConfig
from .confighandler import ConfigHandler

config_handler = ConfigHandler()

def get_config_handler() -> ConfigHandler:
    return config_handler

def get_config(config_name: str) -> BaseConfig:
    # TODO: KeyError handling
    return config_handler.configs[config_name]

def add_config(config: BaseConfig):
    config_handler.add_config(config)
