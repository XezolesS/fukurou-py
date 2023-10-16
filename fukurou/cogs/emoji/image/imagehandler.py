import hashlib
import os
from typing import TypedDict
import requests

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.database import sqlite

class ImageHandler:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.config: EmojiConfig = configs.get_config('emoji')
        self.database = sqlite.EmojiSqlite()

        self.__init_local_directory()

    def __init_local_directory(self):
        if self.config.storage_type != 'local':
            return

        abs_path = os.path.abspath(self.config.storage_dir)
        if not os.path.exists(abs_path):
            os.mkdir(abs_path)
            logger.info('Root image directory created at: %s', abs_path)

        guild_path = os.path.join(abs_path, str(self.guild_id))
        if not os.path.exists(guild_path):
            logger.info('Guild image directory created at: %s', guild_path)
            os.mkdir(guild_path)

        self.directory = guild_path
        logger.info('Image directory for guild(%d) is set to "%s"', self.guild_id, guild_path)

    def __save_local_image(self, file_url: str, ext: str) -> str | None:
        # Download file from url.
        response = requests.get(url=file_url, stream=True, timeout=10)
        image = response.content

        # Build md5 checksum of a file
        checksum = hashlib.md5(image).hexdigest()
        file_name = f'{checksum}.{ext}'

        # Check duplicates
        for file in os.listdir(self.directory):
            if file == file_name:
                logger.error('Image "%s" is already exist in "%s"', file_name, self.directory)

                return None

        # Save
        path = os.path.join(self.directory, file_name)

        with open(path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        logger.info('Image "%s" is saved at "%s"', file_name, self.directory)

        return path

    def save_image(self, name: str, uploader: int, file_url: str, ext: str):
        # Duplicate key check
        database = sqlite.EmojiSqlite()
        emoji = database.get_emoji(guild_id=self.guild_id, name=name)

        if emoji is not None:
            return False

        # Check if the file is image
        if not ext.startswith('image/'):
            return False

        ext = ext.removeprefix('image/')
        file = str()

        match self.config.storage_type:
            case 'local':
                file = self.__save_local_image(file_url=file_url, ext=ext)

        if not file:
            return False

        database.save_emoji(guild_id=self.guild_id,
                            name=name,
                            uploader=uploader,
                            path=file)

    def get_emoji(self, name: str):
        database = sqlite.EmojiSqlite()
        return database.get_emoji(guild_id=self.guild_id, name=name)

class ImageHandlers(TypedDict):
    guild_id: int
    handler: ImageHandler
