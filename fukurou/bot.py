import logging
from typing import Type
import discord
from discord.ext.commands import Bot

from .config import BotConfig
from .configs import add_config, get_config, Config
from .patterns import Singleton

class FukurouMeta(type(Bot), type(Singleton)):
    pass

class FukurouBot(Bot, Singleton, metaclass=FukurouMeta):
    def __init__(self, config: BotConfig):
        self.config = config
        self.logger = logging.getLogger('fukurou')

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            intents = intents,
            command_prefix = '!'
        )

    def add_config(self, config: Type[Config]) -> None:
        """
        Add config to the service.

        :param config: The type of the config. It must be inherited from `BaseConfig`
        :type config: Type[Config]
        """
        add_config(config=config)
        self.logger.info("Config '%s' has been successfully loaded",
            get_config(config=config).file_name
        )

    def run(self) -> None:
        loaded, failed = 0, 0
        for ext in self.config.extensions:
            try:
                self.load_extension(ext)
                self.logger.info("Extension '%s' has been successfully loaded.", ext)
                loaded += 1
            except (
                discord.ExtensionNotFound,
                discord.ExtensionAlreadyLoaded,
                discord.NoEntryPointError,
                discord.ExtensionFailed
            ) as e:
                self.logger.error(e.args[0])
                failed += 1

        self.logger.info(
            'A total of %d extensions were loaded successfully, while %d failed to load.',
            loaded, failed
        )

        super().run(self.config.token)
