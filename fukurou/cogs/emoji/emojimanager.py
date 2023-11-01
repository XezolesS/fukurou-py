import os
import re
import requests
from typing import Final
from discord import Attachment

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.exceptions import (
    EmojiNameExistsError,
    EmojiDatabaseError,
    EmojiFileExistsError,
    EmojiFileDownloadError,
    EmojiFileSaveError,
    EmojiFileTooLargeError,
    EmojiFileTypeError,
    EmojiInvalidNameError,
    EmojiNotFoundError
)
from fukurou.patterns import Singleton
from . import database, storage
from .data import Emoji, EmojiList

ALLOWED_FILETYPES: Final = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
}

class EmojiManager(metaclass=Singleton):
    """
    A class for managing Emoji for the guilds.
    This class is Singleton.
    """
    def __init__(self) -> None:
        self.database = self.__get_database_strategy()
        self.storage = self.__get_storage_strategy()

    def __get_database_strategy(self) -> database.BaseEmojiDatabase | None:
        database_type = configs.get_config('emoji').database_type
        match database_type:
            case 'sqlite':
                return database.EmojiSqlite()

        logger.error('There is no support for database %s.', database_type)
        return None

    def __get_storage_strategy(self) -> storage.BaseEmojiStorage | None:
        storage_type = configs.get_config('emoji').storage_type
        match storage_type:
            case 'local':
                return storage.LocalEmojiStorage()

        logger.error('There is no support for storage %s.', storage_type)
        return None

    def __check_emoji_name(self, emoji_name: str) -> bool:
        pattern = f'^{configs.get_config("emoji").expression_pattern}$'
        return re.match(pattern=pattern, string=emoji_name)

    def __verify_file_type(self, file_type: str) -> str | None:
        if file_type not in ALLOWED_FILETYPES:
            return None

        return file_type.removeprefix('image/')

    def register(self, guild_id: int) -> None:
        """
        Register a guild for Emoji features.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        self.storage.register(guild_id=guild_id)

        logger.info('Guild(%d) is now ready for Emoji.', guild_id)

    def get(self, guild_id: int, emoji_name: str) -> Emoji | None:
        """
        Get Emoji object which has a name of `emoji_name`.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :return: Emoji object, None if there's no such.
        :rtype: Emoji | None
        """
        return self.database.get(guild_id=guild_id, emoji_name=emoji_name)

    def get_file_loc(self, guild_id: int, emoji: Emoji) -> str | os.PathLike:
        """
        Get Emoji file location from `Emoji` object.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji: `Emoji` object.
        :type emoji: Emoji

        :return: Directory, URL or such path like string.
        :rtype: str | os.PathLike
        """
        return os.path.join(self.storage.get_guild_loc(guild_id=guild_id), emoji.file_name)

    def add(self, guild_id: int, emoji_name: str, uploader: int, attachment: Attachment) -> None:
        """
        Add a Emoji for the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        :param uploader: Id of the uploader.
        :type uploader: int
        :param attachment: `discord.Attachment` object of the Emoji image file.
        :type attachment: Attachment

        :raises EmojiInvalidNameError: If Emoji name is not matched with the pattern in config.
        :raises EmojiNameExistsError: If Emoji name is occupied.
        :raises EmojiFileTypeError: If the type of the file is not supported.
        :raises EmojiFileTooLargeError: If the file is too large.
        :raises EmojiFileDownloadError: If failed to download file.
        :raises EmojiFileExistsError: If the identical file is already in the storage.
        :raises EmojiFileSaveError: If failed to save file.
        :raises EmojiDatabaseError: If database operation failed.
        """
        logger.info("""User(%d) uploading emoji: {
                        Name: %s,
                        File URL: %s,
                        File Size: %d Bytes,
                        File Type: %s
                    }""",
                    uploader,
                    emoji_name,
                    attachment.url,
                    attachment.size,
                    attachment.content_type)

        # Check name validity
        if not self.__check_emoji_name(emoji_name=emoji_name):
            raise EmojiInvalidNameError(
                message='Name %s is not matched with the pattern.',
                message_args=(emoji_name,)
            )

        # Check for duplicate name
        emoji = self.database.get(guild_id=guild_id, emoji_name=emoji_name)
        if emoji is not None:
            raise EmojiNameExistsError(
                message='Emoji %s is already exist.',
                message_args=(emoji_name,)
            )

        # Check if the file is image
        ext = self.__verify_file_type(file_type=attachment.content_type)
        if ext is None:
            raise EmojiFileTypeError(
                message='*.%s is invalid file type for Emoji.',
                message_args=(ext,)
            )

        # Check the file size
        if attachment.size > 8*1024*1024:
            raise EmojiFileTooLargeError(
                message='Image file(%.2f MB) is larger than the size limit(%d MB).',
                message_args=(attachment.size/1024/1024, 8,)
            )

        # Download file from url
        try:
            response = requests.get(url=attachment.url, stream=True, timeout=10)
            response.raise_for_status()

            image = response.content
        except requests.exceptions.RequestException as e:
            raise EmojiFileDownloadError(
                e.args,
                message='Error occured while downloading a file.'
            ) from e

        # Save image to the storage
        try:
            file_name = self.storage.save(guild_id=guild_id, file=image, ext=ext)
        except EmojiFileExistsError as e:
            raise EmojiFileExistsError(
                message='Image %s is already exist in %s',
                message_args=(e.file_name, e.directory)
            ) from e
        except EmojiFileSaveError as e:
            raise EmojiFileSaveError(
                e.args,
                message='Error occured while saving a file'
            ) from e

        # Save emoji data to the database
        try:
            self.database.add(guild_id=guild_id,
                              emoji_name=emoji_name,
                              uploader_id=uploader,
                              file_name=file_name)
        except EmojiDatabaseError as e:
            self.storage.delete(guild_id=guild_id, file_name=file_name)

            raise EmojiDatabaseError(
                message='Error occured while saving emoji data: %s',
                message_args=(e.args,)
            ) from e

        logger.info('Emoji "%s" is saved at "%s"', emoji_name, file_name)

    def delete(self, guild_id: int, emoji_name: str) -> None:
        """
        Delete a Emoji from the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :raises EmojiNotFoundError: If there's no such Emoji.
        :raises EmojiDatabaseError: If database operation failed.
        """
        # Check if emoji exists
        emoji = self.database.get(guild_id=guild_id, emoji_name=emoji_name)
        if emoji is None:
            raise EmojiNotFoundError(
                message='There is no emoji named %s',
                message_args=(emoji_name,)
            )

        # Delete emoji record from the database
        try:
            self.database.delete(guild_id=guild_id, emoji_name=emoji_name)
        except EmojiDatabaseError as e:
            raise EmojiDatabaseError(
                message='Error occured while deleting emoji data: %s',
                message_args=(e.args,)
            ) from e

        # Delete image file
        self.storage.delete(guild_id=guild_id, file_name=emoji.file_name)

    def rename(self, guild_id: int, old_name: str, new_name: str) -> None:
        """
        Rename an Emoji.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param old_name: Old name of the Emoji.
        :type old_name: str
        :param new_name: New name of the Emoji.
        :type new_name: str

        :raises EmojiInvalidNameError: If Emoji name is not matched with the pattern in config.
        """
        # Check name validity
        if not self.__check_emoji_name(emoji_name=new_name):
            raise EmojiInvalidNameError(
                message='Name %s is not matched with the pattern.',
                message_args=(new_name,)
            )

        self.database.rename(guild_id=guild_id, old_name=old_name, new_name=new_name)

    def list(self, guild_id: int, keyword: str = None) -> EmojiList:
        """
        Get a list of Emojis in the guild. 
        If keyword is given, search for the Emojis which contain the kewyord in its name.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param keyword: Keyword to search for.
        :type keyword: str, optional

        :return: List of the Emojis.
        :rtype: list[Emoji]
        """
        return self.database.list(guild_id=guild_id, keyword=keyword)

    def increase_usecount(self, guild_id: int, user_id: int, emoji_name: str) -> None:
        """
        Increase an Emoji use count for the user in the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param user_id: Id of the user who used the Emoji.
        :type user_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        """
        self.database.increase_usecount(guild_id=guild_id, user_id=user_id, emoji_name=emoji_name)
