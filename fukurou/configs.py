"""
A module for managing system configs of fukurou and its cogs.
"""
from __future__ import annotations
import os
import logging
import json
from abc import ABC, abstractmethod
from typing import (
    Any,
    TypeVar
)
from dataclasses import asdict

__all__ = [
    'Config',
    'Configurable',
    'NewConfigInterrupt'
]

ConfigT = TypeVar("ConfigT", bound="Config")

FUKUROU_CONFIG_DIR = 'configs/'

class NewConfigInterrupt(BaseException):
    """
    Raised when a new config has been created.
    """

class Config(ABC):
    """
    The base class that all configs must inherit from.

    The config is a `dataclasses.dataclass` and will be saved as a json file.

    To create a config class, you should decorate the class with 
    the `dataclasess.dataclass` and add fields an their default values.
    """
    @classmethod
    def get_file_name(cls) -> str | None:
        return None

    @classmethod
    @abstractmethod
    def from_dict(cls, json_obj: dict[Any]) -> Config:
        raise NotImplementedError

class Configurable:
    """
    The mixin class to add config functionalities to the class.

    The class using this mixin can access to the Config
    (user-written class that inherited from the :class:`Config`) 
    after initialzation. (via calling :meth:`init_config()`)
    """
    __configs: dict[ConfigT, Config] = {}

    def init_config(self, config: ConfigT, interrupt_new: bool = False) -> None:
        """
        Initialize config.
        It will read config file if it exists. Otherwise, create new one with default values.
        You can access to the config through :meth:`get_config()` after initialization.

        It will be ignored when the config is already loaded.

        It will read a certain file under the directory `./config/`. 
        If there's no such config found, create a new config with default options. 

        If `interrupt_new` is set to True, `NewConfigInterrupt` will be 
        raised if a new config is created.

        `IOError` will be raised if something goes wrong while reading a config 
        or writing a new config.

        Parameters
        ----------
        config : ConfigT
            The type of the config. It must be inherited from :class:`BaseConfig`
        interrupt_new : bool, optional
            If it's set to True, :class:`NewConfigInterrupt` will be raised if a new 
            config is created. Set to False by default

        Raises
        ------
        TypeError
            If reading a config or writing a new config is failed
        NewConfigInterrupt
            If a new config is created
        """
        if not issubclass(config, Config):
            raise TypeError('must be inherted from Config.')

        if config in self.__configs:
            # self.logger.warning('%s is already added.', config.__name__)
            return

        # Load config
        os.makedirs(FUKUROU_CONFIG_DIR, exist_ok=True)
        path = os.path.join(FUKUROU_CONFIG_DIR, config.get_file_name())

        try:
            with open(path, mode='r', encoding='utf8') as file:
                content = file.read()
        except FileNotFoundError as e:
            # Write a default config if it's not exist.
            content = json.dumps(asdict(config()), indent=2)

            with open(path, mode='w', encoding='utf8') as file:
                file.write(content)

            if interrupt_new is True:
                raise NewConfigInterrupt from e

        # Register to a config map
        self.__configs[config] = config.from_dict(json.loads(content))

    def get_config(self, config: ConfigT) -> Config | None:
        """
        Get config object.

        Parameters
        ----------
        config : ConfigT
            The type of the config. It must be inherited from :class:`BaseConfig`

        Returns
        -------
        Config | None
            Config object. None if there's no such
        """
        try:
            return self.__configs[config]
        except KeyError:
            return None

    def remove_config(self, config: ConfigT) -> None:
        """
        Remove config.

        Parameters
        ----------
        config : ConfigT
            The type of the config. It must be inherited from :class:`BaseConfig`
        """
        try:
            self.__configs.pop(config)
        except KeyError:
            pass
