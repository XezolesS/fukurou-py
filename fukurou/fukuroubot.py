import discord
from discord.ext.commands import Bot

from . import cogs
from .logging import logger

class FukurouBot(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            intents = intents,
            command_prefix = '!'
        )

def run(token: str):
    bot = FukurouBot()

    for cog in cogs.coglist:
        bot.load_extension(cog)
        logger.info('Extension %s has been successfully loaded.', cog)

    bot.run(token)
