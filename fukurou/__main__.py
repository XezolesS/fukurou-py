import discord
import logging
import json
import os

from configs.fukurou_config import FukurouConfig
import bot

if __name__ == "__main__":
    # Setup logger
    logger = logging.getLogger("Fukurou")
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(filename = "fukurou.log", encoding = "utf-8", mode = "w")
    handler.setFormatter(logging.Formatter("[%(asctime)s | %(levelname)s] %(name)s\t%(message)s"))

    logger.addHandler(handler)

    # Create api_discord.json file to store API keys
    config = FukurouConfig(logger = logger)
    config.init()
    
    # Print invite link
    print(config.getInviteLink())

    # Run bot
    bot.run(token = config.getToken(), logger = logger)

