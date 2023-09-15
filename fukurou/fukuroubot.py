from logging import Logger
import discord
from discord.ext.commands import Bot

from . import cogs

class FukurouBot(Bot):
    def __init__(self, logger: Logger):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            intents = intents,
            command_prefix = '!'
        )

        self.logger = logger

def run(token: str, logger: Logger):
    bot = FukurouBot(logger)

    for cog in cogs.coglist:
        bot.load_extension(cog)
        logger.info('Extension %s has been successfully loaded.', cog)

    bot.run(token)
