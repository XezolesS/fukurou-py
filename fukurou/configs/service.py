import os
import logging
import json
import shutil
from typing import Type, NewType

from fukurou.patterns import SingletonMeta
from .baseconfig import BaseConfig
from .exceptions import NewConfigInterrupt

FUKUROU_CONFIG_DIR = 'configs/'

Config = NewType('Config', BaseConfig)

class ConfigService(metaclass=SingletonMeta):
    def __init__(self):
        self.configs: dict[Type[Config], Config] = {}
        self.logger = logging.getLogger('fukurou.configs')

    def add(self, config: Type[Config], interrupt_new: bool = False) -> None:
        """
        Register and load a config to a ConfigService.
        You can access to configs through :meth:`~get()` method after registering.

        It will be ignored when the config is already loaded.

        It will read a certain file under the directory `./config/`. 
        If there's no such config found, create a new config with default options. 
        
        If `interrupt_new` is set to True, `NewConfigInterrupt` will be 
        raised if a new config is created.

        `IOError` will be raised if something goes wrong while reading a config 
        or writing a new config.

        :param config: The type of the config. It must be inherited from `BaseConfig`
        :type config: Type[Config]
        :param interrupt_new: If it's set to True, `NewConfigInterrupt` will be 
        raised if a new config is created.
        :type interrupt_new: bool

        :raises IOError: If reading a config or writing a new config is failed.
        :raises NewConfigInterrupt: If a new config is created.
        """
        if config in self.configs:
            self.logger.warning('%s is already added.', config.__name__)
            return

        # Instantiate config class
        conf_obj = config()

        # Load config
        path = os.path.join(FUKUROU_CONFIG_DIR, conf_obj.file_name)

        def read():
            os.makedirs(FUKUROU_CONFIG_DIR, exist_ok=True)

            with open(path, mode='r', encoding='utf8') as file:
                content = file.read()

            conf_obj.map(json.loads(content))

        try:
            read()
        except FileNotFoundError as e:
            src = os.path.join(conf_obj.defcon_path)
            shutil.copy2(src, path)

            if interrupt_new is True:
                raise NewConfigInterrupt from e

            read()

        # Register to a config map
        self.configs[config] = conf_obj

    def get(self, config: Type[Config]) -> Config | None:
        """
        Get config object.

        :param config: The type of the config. It must be inherited from `BaseConfig`
        :type config: Type[Config]
        :return: _description_
        :rtype: Config | None
        """
        try:
            return self.configs[config]
        except KeyError:
            return None

def add_config(config: Type[Config], interrupt_new: bool = False) -> None:
    """
    Alias of `ConfigService().add()`
    """
    return ConfigService().add(config=config, interrupt_new=interrupt_new)

def get_config(config: Type[Config]) -> Config | None:
    """
    Alias of `ConfigService().get()`
    """
    return ConfigService().get(config=config)
