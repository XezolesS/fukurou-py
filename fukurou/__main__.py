import discord
import logging
import sys
import json
import os

from . import fukuroubot as fbot
from .configs.fukurou_config import FukurouConfig

if __name__ == "__main__":
    # Setup loggers
    logger = logging.getLogger("Fukurou")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s | %(levelname)s] %(name)s\t%(message)s")

    log_console = logging.StreamHandler(sys.stdout)
    log_console.setLevel(logging.INFO)
    log_console.setFormatter(formatter)

    log_file = logging.FileHandler(filename = "fukurou.log", encoding = "utf-8", mode = "w")
    log_file.setFormatter(formatter)

    logger.addHandler(log_console)
    logger.addHandler(log_file)

    # Create api_discord.json file to store API keys
    config = FukurouConfig(logger = logger)
    config.init()

    # Print invite link
    print(config.getInviteLink())

    # Run bot
    fbot.run(token = config.getToken(), logger = logger)
