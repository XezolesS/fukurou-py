from __future__ import annotations
import os
import logging
import re
from typing import Any, Final, Callable
from functools import wraps
from inspect import signature
import requests
from discord import Attachment
from fukurou.patterns import SingletonMeta

from .database import BaseEmojiDatabase, get_emoji_database
from .storage import BaseEmojiStorage, get_emoji_storage
from .config import EmojiConfig
from .data import Emoji, EmojiList
from .exceptions import (
    EmojiError,
    EmojiNameExistsError,
    EmojiDatabaseError,
    EmojiFileExistsError,
    EmojiFileDownloadError,
    EmojiFileSaveError,
    EmojiFileTooLargeError,
    EmojiFileTypeError,
    EmojiCapacityExceededError,
    EmojiInvalidNameError,
    EmojiNotFoundError
)

ALLOWED_FILETYPES: Final = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
}

def connected(func):
    """
    Check if database and storage are connected. 
    It can be used as a decorator `@connected` to the method. 
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        params = signature(func).bind(*args, **kwargs).arguments
        self: EmojiManager = params['self']

        if not isinstance(self.database, BaseEmojiDatabase):
            raise EmojiError(message='Database Offline')

        if not isinstance(self.storage, BaseEmojiStorage):
            raise EmojiError(message='Storage Offline')

        return func(*args, **kwargs)
    return wrapper

def check_emoji_name(argname: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            emoji_name = params[argname]

            pattern = self.config.expression.name_pattern

            if not re.match(pattern=pattern, string=emoji_name):
                raise EmojiInvalidNameError(
                    message='Name %s is not matched with the pattern.',
                    message_args=(emoji_name,)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_emoji_new(argname: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            emoji_name = params[argname]

            if self.database.exists(guild_id=guild_id, emoji_name=emoji_name):
                raise EmojiNameExistsError(
                    message='Emoji %s is already exist.',
                    message_args=(emoji_name,)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_emoji_exists(argname: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            emoji_name = params[argname]

            if not self.database.exists(guild_id=guild_id, emoji_name=emoji_name):
                raise EmojiNotFoundError(
                    message='There is no emoji named %s',
                    message_args=(emoji_name,)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_file_type(argname: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            attachment = params[argname]

            if attachment.content_type not in ALLOWED_FILETYPES:
                raise EmojiFileTypeError(
                    message='*.%s is invalid file type for Emoji.',
                    message_args=(attachment.content_type,)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_file_size(argname: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            attachment = params[argname]
            maxsize = self.config.constraints[guild_id].maxsize

            if attachment.size > maxsize*1024:
                raise EmojiFileTooLargeError(
                    message='Image file(%.2f KB) is larger than the size limit(%d KB).',
                    message_args=(attachment.size/1024, maxsize)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_capacity_limit():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            capacity = self.config.constraints[guild_id].capacity

            if capacity == -1:
                return

            if self.database.count(guild_id=guild_id) >= capacity:
                raise EmojiCapacityExceededError(
                    message='The capacity limit exceeded. (Max %d)',
                    message_args=(capacity)
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

class EmojiManager(metaclass=SingletonMeta):
    """
    A class for managing Emoji for the guilds.
    This class is Singleton.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger('fukurou.emoji')
        self.config = EmojiConfig()

        self.database = None
        try:
            self.database = get_emoji_database(dbtype=self.config.database.type)
        except ValueError as e:
            self.logger.error(
                'Failed to assign database for Emoji (%s %s)',
                e.args[0], e.args[1]
            )

        self.storage = None
        try:
            self.storage = get_emoji_storage(sttype=self.config.storage.type)
        except ValueError as e:
            self.logger.error(
                'Failed to assign storage for Emoji (%s %s)',
                e.args[0], e.args[1]
            )

    def register(self, guild_id: int) -> None:
        """
        Register a guild for Emoji features.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        self.storage.register(guild_id=guild_id)

        self.logger.info('Guild(%d) is now ready for Emoji.', guild_id)

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

    @connected
    @check_emoji_name(argname='emoji_name')
    @check_emoji_new(argname='emoji_name')
    @check_file_type(argname='attachment')
    @check_file_size(argname='attachment')
    @check_capacity_limit()
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
        self.logger.info('User(%d) is uploading emoji "%s"', uploader, emoji_name)
        self.logger.debug('Detail: {Name: %s, File URL: %s, File Size: %d Bytes, File Type: %s}',
                          emoji_name,
                          attachment.url,
                          attachment.size,
                          attachment.content_type)
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
            file_name = self.storage.save(
                guild_id=guild_id,
                file=image,
                ext=attachment.content_type.removeprefix('image/')
            )
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

        self.logger.info('Emoji "%s" is saved at "%s"', emoji_name, file_name)

    @connected
    @check_emoji_exists(argname='emoji_name')
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
        emoji = self.database.get(guild_id=guild_id, emoji_name=emoji_name)

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

    @connected
    @check_emoji_exists(argname='old_name')
    @check_emoji_name(argname='new_name')
    @check_emoji_new(argname='new_name')
    def rename(self, guild_id: int, old_name: str, new_name: str) -> None:
        """
        Rename an Emoji.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param old_name: Old name of the Emoji.
        :type old_name: str
        :param new_name: New name of the Emoji.
        :type new_name: str
        
        :raises EmojiNotFoundError: If there's no such Emoji.
        :raises EmojiInvalidNameError: If Emoji name is not matched with the pattern in config.
        """
        self.database.rename(guild_id=guild_id, old_name=old_name, new_name=new_name)

    @connected
    @check_emoji_exists(argname='emoji_name')
    @check_file_type(argname='attachment')
    @check_file_size(argname='attachment')
    def replace(self,
                guild_id: int,
                emoji_name: str,
                uploader: int,
                attachment: Attachment) -> None:
        """
        Replace an image of the Emoji.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        :param uploader: Id of the uploader.
        :type uploader: int
        :param attachment: `discord.Attachment` object of the Emoji image file.
        :type attachment: Attachment

        :raises EmojiNotFoundError: If there's no such Emoji.
        :raises EmojiFileTypeError: If the type of the file is not supported.
        :raises EmojiFileTooLargeError: If the file is too large.
        :raises EmojiFileDownloadError: If failed to download file.
        :raises EmojiFileExistsError: If the identical file is already in the storage.
        :raises EmojiFileSaveError: If failed to save file.
        :raises EmojiDatabaseError: If database operation failed.
        """
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
            file_name = self.storage.save(
                guild_id=guild_id,
                file=image,
                ext=attachment.content_type.removeprefix('image/')
            )
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

        old_emoji = self.database.get(guild_id=guild_id, emoji_name=emoji_name)

        # Replace emoji file_name from the database
        try:
            self.database.replace(guild_id=guild_id,
                                  emoji_name=emoji_name,
                                  uploader_id=uploader,
                                  file_name=file_name)
        except EmojiDatabaseError as e:
            self.storage.delete(guild_id=guild_id, file_name=file_name)

            raise EmojiDatabaseError(
                message='Error occured while saving emoji data: %s',
                message_args=(e.args,)
            ) from e

        # Delete old emoji file
        self.storage.delete(guild_id=guild_id, file_name=old_emoji.file_name)

    @connected
    def list(self, user_id: int, guild_id: int, keyword: str = None) -> EmojiList:
        """
        Get a list of Emojis with its details in the guild. 
        The details both for the user and the guild will be retrieved. 

        If `keyword` is given, only the Emojis which contain
        the kewyord in its name will be retrieved.

        :param user_id: Id of the user.
        :type user_id: int
        :param guild_id: Id of the guild.
        :type guild_id: int
        :param keyword: Keyword to search for.
        :type keyword: str, optional

        :return: List of the Emojis.
        :rtype: EmojiList
        """
        return self.database.list(user_id=user_id, guild_id=guild_id, keyword=keyword)

    @connected
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
