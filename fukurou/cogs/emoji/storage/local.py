import os
from os import PathLike

from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.exceptions import EmojiFileIOError
from .base import BaseEmojiStorage

class LocalEmojiStorage(BaseEmojiStorage):
    def _setup(self):
        root_dir = EmojiConfig().storage.directory
        abs_root_dir = os.path.abspath(root_dir)

        try:
            os.makedirs(abs_root_dir)
            self.logger.info('An Emoji storage has been created at: %s', abs_root_dir)
        except FileExistsError:
            self.logger.info('An Emoji stroage is located at: %s', abs_root_dir)
        except OSError as e:
            self.logger.error('Error occured while setting up Emoji storage: %s', e.strerror)
        finally:
            self.directory = abs_root_dir

    def get_guild_loc(self, guild_id: int) -> str | PathLike:
        return os.path.join(self.directory, str(guild_id))

    def register(self, guild_id: int):
        guild_dir = self.get_guild_loc(guild_id=guild_id)

        try:
            os.makedirs(guild_dir)
            self.logger.info('Registered a new Emoji storage for guild(%d).', guild_id)
        except FileExistsError:
            self.logger.info('Found a registered Emoji storage for guild(%d).', guild_id)
        except OSError as e:
            self.logger.error('Error occured while registering Emoji storage for guild(%d): %s',
                              guild_id, e.strerror)

    def get(self, guild_id: int, file_name: str, **kwargs) -> str | PathLike:
        guild_dir = self.get_guild_loc(guild_id=guild_id)
        return os.path.join(guild_dir, file_name)

    def save(self, guild_id: int, file: bytes, file_name: str, **kwargs) -> None:
        file_path = self.get(guild_id=guild_id, file_name=file_name)

        # Save a file to the local storage
        try:
            with open(file_path, 'wb') as f:
                f.write(file)
        except OSError as e:
            self.logger.error('Error occured while saving file.', exc_info=1)
            raise EmojiFileIOError('w', *e.args) from e

        return file_name

    def delete(self, guild_id: int, file_name: str, **kwargs) -> None:
        file_path = self.get(guild_id=guild_id, file_name=file_name)

        try:
            os.remove(path=file_path)
        except FileNotFoundError:
            self.logger.warning('Cannot find file to remove: %s', file_path)
        except OSError as e:
            self.logger.error('Error occured while removing file.', exc_info=1)
            raise EmojiFileIOError('w', *e.args) from e
