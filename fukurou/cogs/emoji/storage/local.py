import os
from os import PathLike
import hashlib

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.exceptions import (
    EmojiFileDeleteError,
    EmojiFileExistsError,
    EmojiFileNotFoundError,
    EmojiFileSaveError
)
from .base import BaseEmojiStorage

class LocalEmojiStorage(BaseEmojiStorage):
    def _setup(self):
        root_dir = configs.get_config('emoji').storage_dir
        abs_root_dir = os.path.abspath(root_dir)

        try:
            os.makedirs(abs_root_dir)
            logger.info('An Emoji storage has been created at: %s', abs_root_dir)
        except FileExistsError:
            logger.info('An Emoji stroage is located at: %s', abs_root_dir)
        except OSError as e:
            logger.error('Error occured while setting up Emoji storage: %s', e.strerror)
        finally:
            self.directory = abs_root_dir

    def get_guild_loc(self, guild_id: int) -> str | PathLike:
        return os.path.join(self.directory, str(guild_id))

    def register(self, guild_id: int):
        guild_dir = self.get_guild_loc(guild_id=guild_id)

        try:
            os.makedirs(guild_dir)
            logger.info('Registered a new Emoji storage for guild(%d).', guild_id)
        except FileExistsError:
            logger.info('Found a registered Emoji storage for guild(%d).', guild_id)
        except OSError as e:
            logger.error('Error occured while registering Emoji storage for guild(%d): %s',
                         guild_id, e.strerror)

    def get(self, guild_id: int, file_name: str, **kwargs) -> str | PathLike:
        guild_dir = self.get_guild_loc(guild_id=guild_id)
        return os.path.join(guild_dir, file_name)

    def save(self, guild_id: int, file: bytes, ext: str, **kwargs) -> str:
        # Build md5 checksum of a file
        checksum = hashlib.md5(file).hexdigest()
        file_name = f'{checksum}.{ext}'

        # Check if file already exists
        file_path = self.get(guild_id=guild_id, file_name=file_name)
        if os.path.exists(file_path):
            raise EmojiFileExistsError(file_name=file_name, directory=self.directory)

        # Save a file to the local storage
        try:
            with open(file_path, 'wb') as f:
                f.write(file)
        except OSError as e:
            raise EmojiFileSaveError() from e

        return file_name

    def delete(self, guild_id: int, file_name: str, **kwargs) -> None:
        file_path = self.get(guild_id=guild_id, file_name=file_name)

        try:
            os.remove(path=file_path)
        except FileNotFoundError as e:
            raise EmojiFileNotFoundError() from e
        except OSError as e:
            raise EmojiFileDeleteError() from e
