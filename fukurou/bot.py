import logging
import discord
from discord.ext.commands import Bot

from .config import BotConfig
from .patterns import Singleton

class FukurouMeta(type(Bot), type(Singleton)):
    pass

class FukurouBot(Bot, Singleton, metaclass=FukurouMeta):
    def __init__(self):
        self.logger = logging.getLogger('fukurou')

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            intents = intents,
            command_prefix = '!'
        )

    def run(self):
        config = BotConfig()

        loaded = 0
        failed = 0
        for ext in config.extensions:
            try:
                self.load_extension(ext)
                self.logger.info('Extension %s has been successfully loaded.', ext)
                loaded += 1
            except discord.ExtensionNotFound as e:
                self.logger.error(e.args[0])
                failed += 1
            except discord.ExtensionAlreadyLoaded as e:
                self.logger.error(e.args[0])
                failed += 1
            except discord.NoEntryPointError as e:
                self.logger.error(e.args[0])
                failed += 1
            except discord.ExtensionFailed as e:
                self.logger.error(e.args[0])
                failed += 1

        self.logger.info(
            'A total of %d extensions were loaded successfully, while %d failed to load.',
            loaded, failed
        )

        super().run(config.token)
