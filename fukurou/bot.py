import logging
import logging.config
import discord

from discord.ext.commands import Bot

from fukurou.bot_config import BotConfig
from fukurou.configs import ConfigMixin

class FukurouBot(ConfigMixin, Bot):
    def __init__(self, *args, **kwargs):
        # Initialize every super classes but the Bot.
        ConfigMixin.__init__(self, *args, **kwargs)

        self.init_config(BotConfig, interrupt_new=True)

        self.config: BotConfig = self.get_config(BotConfig)
        logging.config.dictConfig(self.config.logging)

        self.logger = logging.getLogger('fukurou')

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        Bot.__init__(
            self,
            intents = intents,
            command_prefix = '!',
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
