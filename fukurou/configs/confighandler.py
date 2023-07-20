import logging

from . import BaseConfig

class ConfigHandler:
    @property
    def directory(self) -> str:
        return "configs"

    @property
    def configs(self) -> dict[str, BaseConfig]:
        return self.__configs

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger
        self.__configs: list[str, BaseConfig] = dict()

    def add_config(self, config: BaseConfig):
        config.load(self.directory)
        self.configs[config.name] = config
