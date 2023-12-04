import sys

from .configs import SystemConfig, NewConfigInterrupt
from .logging import TempLogger
from .fukuroubot import FukurouBot

CONFIG_CREATED_MESSAGE = """ERROR: Config not found.

New config has been created at "configs/fukurou.json".
Run the program again after modifying it."""

if __name__ == '__main__':
    # Load system config
    try:
        SystemConfig().load(interrupt_new=True)
    except NewConfigInterrupt:
        print(CONFIG_CREATED_MESSAGE)
        sys.exit()

    TempLogger().init()

    FukurouBot().run()
