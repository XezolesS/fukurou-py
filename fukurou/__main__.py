import sys

from fukurou.configs import NewConfigInterrupt
from .bot import FukurouBot

CONFIG_CREATED_MESSAGE = """ERROR: Config not found.

New config has been created at "configs/fukurou.json".
Run the program again after modifying it."""

if __name__ == '__main__':
    try:
        bot = FukurouBot()
        bot.run()
    except NewConfigInterrupt:
        print(CONFIG_CREATED_MESSAGE)
        sys.exit()
