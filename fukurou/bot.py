import discord
from discord.ext.commands import Bot
from logging import Logger

class Fukurou(Bot):
    def __init__(self, token: str, logger: Logger):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            intents = intents,
            command_prefix = "!"
        )
        
        super().load_extension("cogs.greetings")
        
        self.token = token
        self.logger = logger


    def run(self):
        super().run(self.token)

    
def run(token: str, logger: Logger):
    Fukurou(token, logger).run()