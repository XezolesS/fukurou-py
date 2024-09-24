from __future__ import annotations
import os
import io
import logging
import re
import hashlib
import asyncio
from typing import Final
from functools import wraps
from inspect import signature
import requests
from discord import Attachment

from fukurou.cogs.emoji.database import BaseEmojiDatabase, get_emoji_database
from fukurou.cogs.emoji.storage import BaseEmojiStorage, get_emoji_storage
from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.data import Emoji, EmojiList
from fukurou.cogs.emoji.exceptions import (
    EmojiCapacityExceededError,
    EmojiDatabaseError,
    EmojiExistsError,
    EmojiFileDownloadError,
    EmojiFileExistsError,
    EmojiFileIOError,
    EmojiFileTooLargeError,
    EmojiFileTypeError,
    EmojiInvalidNameError,
    EmojiNotFoundError,
    EmojiNotReadyError,
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
            raise EmojiNotReadyError('Database')

        if not isinstance(self.storage, BaseEmojiStorage):
            raise EmojiNotReadyError('Storage')

        return func(*args, **kwargs)
    return wrapper

def check_emoji_name(argname: str):
    """
    Check if an emoji name matches the pattern.

    :param argname: Name of the parameter, representing `Name of the Emoji`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            emoji_name = params[argname]

            pattern = self.config.expression.name_pattern
            logging.getLogger('').debug(pattern)

            if not re.match(pattern=pattern, string=emoji_name):
                raise EmojiInvalidNameError(emoji_name, pattern)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_emoji_isnew(argname: str):
    """
    Check if an emoji name is not recorded in the database.

    :param argname: Name of the parameter, representing `Name of the Emoji`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            emoji_name = params[argname]

            if self.database.exists(guild_id=guild_id, emoji_name=emoji_name):
                raise EmojiExistsError(emoji_name)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_emoji_exists(argname: str):
    """
    Check if an emoji name already exists in the database.

    :param argname: Name of the parameter, representing `Name of the Emoji`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            emoji_name = params[argname]

            if not self.database.exists(guild_id=guild_id, emoji_name=emoji_name):
                raise EmojiNotFoundError(emoji_name)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_file_type(argname: str):
    """
    Check for the type of an attachment file.

    :param argname: Name of the parameter, representing `Attachment`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            attachment = params[argname]

            if attachment.content_type not in ALLOWED_FILETYPES:
                raise EmojiFileTypeError(attachment.content_type)

            kwargs['file_type'] = attachment.content_type.removeprefix('image/')

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_file_size(argname: str):
    """
    Check for the size of an attachment file.

    :param argname: Name of the parameter, representing `Attachment`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            attachment = params[argname]
            maxsize = self.config.constraints[guild_id].maxsize

            if attachment.size > maxsize*1024:
                raise EmojiFileTooLargeError(attachment.size/1024, maxsize)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_file_isnew(argname: str):
    """
    Check if an attachment is already exists in the storage.
    The method to be wrapped is must asynchronous.

    This decorator adds additional keyword arguments:
    - `file_byte`: The byte-data of the attachment file.
    - `file_hash`: The md5 hash of the attachment file.
    - `file_name`: The name of the file which is going to be stored to.

    :param argname: Name of the parameter, representing `Attachment`.
    :type argname: str
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            attachment: Attachment = params[argname]

            # Save attachment to buffer
            buffer = io.BytesIO()
            try:
                await attachment.save(fp=buffer)
            except requests.exceptions.RequestException as e:
                raise EmojiFileDownloadError(*e.args) from e

            # Add additional arguments to prevent reading attachment again
            kwargs['file_byte'] = buffer.read()
            kwargs['file_hash'] = hashlib.md5(kwargs['file_byte']).hexdigest()
            kwargs['file_name'] = f"{kwargs['file_hash']}.{kwargs['file_type']}"

            emoji_name = self.database.file_exists(guild_id=guild_id, file_name=kwargs['file_name'])
            if emoji_name is not None:
                raise EmojiFileExistsError(emoji_name)

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_capacity_limit():
    """
    Check for the guild's emoji capacity limit.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = signature(func).bind(*args, **kwargs).arguments
            self: EmojiManager = params['self']
            guild_id = params['guild_id']
            capacity = self.config.constraints[guild_id].capacity

            if capacity == -1:
                return func(*args, **kwargs)

            if self.database.count(guild_id=guild_id) >= capacity:
                raise EmojiCapacityExceededError(capacity)

            return func(*args, **kwargs)
        return wrapper
    return decorator

class EmojiManager:
    """
    A class for managing Emoji for the guilds.
    This class is Singleton.
    """
    def __init__(self, config: EmojiConfig) -> None:
        self.logger = logging.getLogger('fukurou.emoji')
        self.config: EmojiConfig = config
        self.database = get_emoji_database(config)
        self.storage = get_emoji_storage(config)

    def register(self, guild_id: int) -> None:
        """
        Register a guild for Emoji features.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        if not isinstance(self.storage, BaseEmojiStorage):
            self.logger.error(
                'Cannot register an Emoji storage for the guild(%d): Invalid Storage Type',
                guild_id
            )
            return

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
    @check_emoji_isnew(argname='emoji_name')
    @check_file_type(argname='attachment')
    @check_file_size(argname='attachment')
    @check_file_isnew(argname='attachment')
    @check_capacity_limit()
    async def add(self,
                  guild_id: int,
                  emoji_name: str,
                  uploader: int,
                  attachment: Attachment,
                  **kwargs) -> None:
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
        # Save image to the storage
        try:
            self.storage.save(
                guild_id=guild_id,
                file=kwargs['file_byte'],
                file_name=kwargs['file_name']
            )
        except EmojiFileIOError as e:
            raise EmojiFileIOError(*e.args) from e

        # Save emoji data to the database
        try:
            self.database.add(guild_id=guild_id,
                              emoji_name=emoji_name,
                              uploader_id=uploader,
                              file_name=kwargs['file_name'])
        except EmojiDatabaseError as e:
            self.storage.delete(guild_id=guild_id, file_name=kwargs['file_name'])
            raise EmojiDatabaseError(*e.args) from e

        self.logger.info('Emoji "%s" is saved at "%s"', emoji_name, kwargs['file_name'])

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
            raise EmojiDatabaseError(*e.args) from e

        # Delete image file
        self.storage.delete(guild_id=guild_id, file_name=emoji.file_name)

    @connected
    @check_emoji_exists(argname='old_name')
    @check_emoji_name(argname='new_name')
    @check_emoji_isnew(argname='new_name')
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
    @check_file_isnew(argname='attachment')
    async def replace(self,
                guild_id: int,
                emoji_name: str,
                uploader: int,
                attachment: Attachment,
                **kwargs) -> None:
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
        # Save image to the storage
        try:
            self.storage.save(
                guild_id=guild_id,
                file=kwargs['file_byte'],
                file_name=kwargs['file_name']
            )
        except EmojiFileIOError as e:
            raise EmojiFileIOError(*e.args) from e

        old_emoji = self.database.get(guild_id=guild_id, emoji_name=emoji_name)

        # Replace emoji file_name from the database
        try:
            self.database.replace(guild_id=guild_id,
                                  emoji_name=emoji_name,
                                  uploader_id=uploader,
                                  file_name=kwargs['file_name'])
        except EmojiDatabaseError as e:
            self.storage.delete(guild_id=guild_id, file_name=kwargs['file_name'])
            raise EmojiDatabaseError(*e.args) from e

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
