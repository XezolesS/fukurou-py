import discord
from discord.ext.commands import Bot

from . import cogs
from .configs import SystemConfig
from .logging import TempLogger
from .patterns import Singleton

class FukurouMeta(type(Bot), type(Singleton)):
    pass

class FukurouBot(Bot, Singleton, metaclass=FukurouMeta):
    def __init__(self):
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
            TempLogger().logger.info('Extension %s has been successfully loaded.', cog)

        super().run(SystemConfig().token)
