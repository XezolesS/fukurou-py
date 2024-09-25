"""
A module for managing system configs of fukurou and its cogs.
"""
from __future__ import annotations
import os
import json
from abc import ABC
from typing import Any
import inspect
import dataclasses

__all__ = [
    'Config',
    'Configurable',
    'NewConfigInterrupt'
]

FUKUROU_CONFIG_DIR = 'configs/'

class NewConfigInterrupt(BaseException):
    """
    Raised when a new config has been created.
    """

class Config(ABC):
    @classmethod
    def get_file_name(cls) -> str | None:
        return None

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> Config:
        params = {}
        for field in dataclasses.fields(cls):
            key = field.name

            if inspect.isclass(field.default_factory):
                if issubclass(field.default_factory, Config):
                    value = field.default_factory.from_dict(json_obj[key])
                else:
                    value = field.default_factory(json_obj[key])
            else:
                value = json_obj[key]

            params[key] = value

        return cls(**params)

class Configurable:
    """
    The mixin class to add config functionalities to the class.

    The class using this mixin can access to the Config
    (user-written class that inherited from the :class:`Config`) 
    after initialzation. (via calling :meth:`init_config()`)
    """
    __configs: dict[type[Config], Config] = {}

    def init_config(self, config: type[Config], interrupt_new: bool = False) -> None:
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
        config : type[Config]
            The type of the config. It must be inherited from :class:`Config`
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
            content = json.dumps(dataclasses.asdict(config()), indent=2)

            with open(path, mode='w', encoding='utf8') as file:
                file.write(content)

            if interrupt_new is True:
                raise NewConfigInterrupt from e

        # Register to a config map
        self.__configs[config] = config.from_dict(json.loads(content))

    def get_config(self, config: type[Config]) -> Config | None:
        """
        Get config object.

        Parameters
        ----------
        config : type[Config]
            The type of the config. It must be inherited from :class:`Config`

        Returns
        -------
        Config | None
            Config object. None if there's no such
        """
        try:
            return self.__configs[config]
        except KeyError:
            return None

    def remove_config(self, config: type[Config]) -> None:
        """
        Remove config.

        Parameters
        ----------
        config : type[Config]
            The type of the config. It must be inherited from :class:`BaseConfig`
        """
        try:
            self.__configs.pop(config)
        except KeyError:
            pass