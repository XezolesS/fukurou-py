import logging
import discord
from discord.ext.commands import Bot

from . import cogs
from .configs import SystemConfig
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
        for cog in cogs.coglist:
            self.load_extension(cog)
            self.logger.info('Extension %s has been successfully loaded.', cog)

        super().run(SystemConfig().token)
