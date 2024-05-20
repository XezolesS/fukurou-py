import sys
import logging
import logging.config

from .configs import NewConfigInterrupt
from .config import BotConfig
from .bot import FukurouBot

CONFIG_CREATED_MESSAGE = """ERROR: Config not found.

New config has been created at "configs/fukurou.json".
Run the program again after modifying it."""

if __name__ == '__main__':
    # Load system config
    try:
        BotConfig().load(interrupt_new=True)
    except NewConfigInterrupt:
        print(CONFIG_CREATED_MESSAGE)
        sys.exit()

    # Load logging config
    logging.config.dictConfig(BotConfig().logging)

    FukurouBot().run()
