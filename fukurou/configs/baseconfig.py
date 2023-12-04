import os
import json
import shutil
from abc import ABC, abstractmethod
from typing import Any

from fukurou.patterns import Singleton
from .exceptions import NewConfigInterrupt

FUKUROU_CONFIG_DIR = 'configs/'

class BaseConfigMeta(type(ABC), type(Singleton)):
    pass

class BaseConfig(ABC, Singleton, metaclass=BaseConfigMeta):
    """
    Abstract class for the config. 
    Property `file_name` and method `__map()` must be implemented.

    The name of the default config must be a form of `defcon_{file_name}`.
    Default config must be located under `data/` in the same directory of the source code.

    :cvar file_name: Name of the config file.
    """
    @property
    @abstractmethod
    def file_name(self) -> str:
        """
        Name of the config file.
        """
        raise NotImplementedError

    def __init__(self, defcon_dir: str = __file__):
        self.defcon_dir = os.path.join(os.path.dirname(defcon_dir), 'data')

    def load(self, interrupt_new: bool = False) -> None:
        """
        Load a specific config under the directory `./config/`. 
        If there's no config found, create a new config with default options. 
        
        If interrupt_new is set to True, `NewConfigInterrupt` will be 
        raised if a new config is created.

        `IOError` will be raised if something goes wrong while reading a config 
        or writing a new config.

        :raises IOError: If reading a config or writing a new config is failed.
        :raises NewConfigInterrupt: If a new config is created.
        """
        path = os.path.join(FUKUROU_CONFIG_DIR, self.file_name)

        def read():
            with open(path, mode='r', encoding='utf8') as file:
                content = file.read()

            self.map(json.loads(content))

        try:
            read()
        except FileNotFoundError as e:
            src = os.path.join(self.defcon_dir, 'defcon_' + self.file_name)

            shutil.copy2(src, path)

            if interrupt_new is True:
                raise NewConfigInterrupt from e

            read()

    @abstractmethod
    def map(self, json_obj: dict[Any]) -> None:
        raise NotImplementedError
