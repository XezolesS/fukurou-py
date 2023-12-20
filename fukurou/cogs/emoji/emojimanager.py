from __future__ import annotations
import os
import logging
import re
from typing import Any, Final, Callable
import requests
from discord import Attachment
from fukurou.patterns import SingletonMeta

from . import database, storage
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

class EmojiManager(metaclass=SingletonMeta):
    """
    A class for managing Emoji for the guilds.
    This class is Singleton.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger('fukurou.emoji')
        self.config = EmojiConfig()
        self.database = self.__get_database_strategy()
        self.storage = self.__get_storage_strategy()

    def __get_database_strategy(self) -> database.BaseEmojiDatabase | None:
        database_type = self.config.database.type
        match database_type:
            case 'sqlite':
                return database.EmojiSqlite()

        self.logger.error('There is no support for database %s.', database_type)
        return None

    def __get_storage_strategy(self) -> storage.BaseEmojiStorage | None:
        storage_type = self.config.storage.type
        match storage_type:
            case 'local':
                return storage.LocalEmojiStorage()

        self.logger.error('There is no support for storage %s.', storage_type)
        return None

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
        # Data validation
        try:
            EmojiValidator(
                database=self.database,
                guild_id=guild_id,
                emoji_name=emoji_name,
                attachment=attachment
            ) \
            .addval_name_pattern(pattern=f'^{self.config.expression.name_pattern}$') \
            .addval_emoji_new() \
            .addval_file_type() \
            .addval_file_size(maxsize=self.config.constraints[guild_id].maxsize) \
            .addval_capacity_limit(capacity=self.config.constraints[guild_id].capacity) \
            .validate()
        except EmojiError as e:
            raise e

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
        # Data validation
        try:
            EmojiValidator(
                database=self.database,
                guild_id=guild_id,
                emoji_name=emoji_name
            ) \
            .addval_emoji_exists() \
            .validate()
        except EmojiError as e:
            raise e

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
        # Data validation
        try:
            EmojiValidator(
                database=self.database,
                guild_id=guild_id
            ) \
            .set_emoji_name(emoji_name=old_name) \
            .addval_emoji_exists() \
            .set_emoji_name(emoji_name=new_name) \
            .addval_name_pattern(pattern=f'^{self.config.expression.name_pattern}$') \
            .addval_emoji_new() \
            .validate()
        except EmojiError as e:
            raise e

        self.database.rename(guild_id=guild_id, old_name=old_name, new_name=new_name)

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
        # Data validation
        try:
            EmojiValidator(
                database=self.database,
                guild_id=guild_id,
                emoji_name=emoji_name,
                attachment=attachment
            ) \
            .addval_emoji_exists() \
            .addval_file_type() \
            .addval_file_size(maxsize=self.config.constraints[guild_id].maxsize) \
            .validate()
        except EmojiError as e:
            raise e

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

class EmojiValidator:
    """
    A class for building validation process and validating Emoji data. 
    Each validator will raise error if specific conditions are not satisfied.
    """
    def __init__(self,
                 database: database.BaseEmojiDatabase | None = None,
                 guild_id: int | None = None,
                 emoji_name: str | None = None,
                 attachment: Attachment | None = None):
        self.__validators = []
        self.__database = database
        self.__guild_id = guild_id
        self.__emoji_name = emoji_name
        self.__attachment = attachment

    def __add_validator(self, func: Callable, kwargs: dict[Any] = {}):
        self.__validators.append({'func': func, 'kwargs': kwargs})

    def set_database(self, database: database.BaseEmojiDatabase) -> EmojiValidator:
        """
        Set the database to validator to use.

        :param database: Emoji database object.
        :type database: database.BaseEmojiDatabase
        """
        self.__database = database

        return self

    def set_guild_id(self, guild_id: int) -> EmojiValidator:
        """
        Set a guild Id to the validator.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        self.__guild_id = guild_id

        return self

    def set_emoji_name(self, emoji_name: str) -> EmojiValidator:
        """
        Set the name of the Emoji to validate.

        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        """
        self.__emoji_name = emoji_name

        return self

    def set_attachment(self, attachment: Attachment) -> EmojiValidator:
        """
        Set the attachment to validate.

        :param attachment: discord.Attachment object.
        :type attachment: discord.Attachment
        """
        self.__attachment = attachment

        return self

    def addval_name_pattern(self, pattern: str) -> EmojiValidator:
        """
        Add a validator to check if Emoji name is matched with the pattern.

        The validator must have this property before validation. 
        - `emoji_name`: Name of the Emoji.
        
        :class:`EmojiInvalidNameError` will be raised if:
        - `emoji_name` is None.
        - `emoji_name` is not matched with the `pattern`.

        :param pattern: Regex pattern to be matched with.
        :type pattern: str

        :return: self
        :rtype: EmojiValidator
        """
        def validate_name_pattern(emoji_name: str, pattern: str):
            conditions = [
                emoji_name is None,
                not re.match(pattern=pattern, string=emoji_name)
            ]

            if any(conditions):
                raise EmojiInvalidNameError(
                    message='Name %s is not matched with the pattern.',
                    message_args=(emoji_name,)
                )

        self.__add_validator(
            validate_name_pattern,
            {
                'emoji_name': self.__emoji_name,
                'pattern': pattern
            }
        )

        return self

    def addval_emoji_new(self) -> EmojiValidator:
        """
        Add a validator to check if the Emoji is not in the database.

        The validator must have this property before validation. 
        - `database`: Emoji database to search for.
        - `guild_id`: Id of the guild.
        - `emoji_name`: Name of the Emoji.
        
        :class:`EmojiNameExistsError` will be raised if:
        - `database`, `guild_id` or `emoji_name` is None.
        - There's an Emoji record that matched with the 
        `guild_id` and `emoji_name` in the `database`.

        :return: self
        :rtype: EmojiValidator
        """
        def validate_name_new(database: database.BaseEmojiDatabase,
                              guild_id: int,
                              emoji_name: str):
            conditions = [
                None in (database, guild_id, emoji_name),
                database.exists(guild_id=guild_id, emoji_name=emoji_name)
            ]

            if any(conditions):
                raise EmojiNameExistsError(
                    message='Emoji %s is already exist.',
                    message_args=(emoji_name,)
                )

        self.__add_validator(
            validate_name_new,
            {
                'database': self.__database,
                'guild_id': self.__guild_id,
                'emoji_name': self.__emoji_name
            }
        )

        return self

    def addval_emoji_exists(self) -> EmojiValidator:
        """
        Add a validator to check if the Emoji exists.

        The validator must have this property before validation. 
        - `database`: Emoji database to search for.
        - `guild_id`: Id of the guild.
        - `emoji_name`: Name of the Emoji.
        
        :class:`EmojiNotFoundError` will be raised if:
        - `database`, `guild_id` or `emoji_name` is None.
        - There's no Emoji record that matched with the 
        `guild_id` and `emoji_name` in the `database`.

        :return: self
        :rtype: EmojiValidator
        """
        def validate_emoji_exists(database: database.BaseEmojiDatabase,
                                  guild_id: int,
                                  emoji_name: str):
            conditions = [
                None in (database, guild_id, emoji_name),
                not database.exists(guild_id=guild_id, emoji_name=emoji_name)
            ]

            if any(conditions):
                raise EmojiNotFoundError(
                    message='There is no emoji named %s',
                    message_args=(emoji_name,)
                )

        self.__add_validator(
            validate_emoji_exists,
            {
                'database': self.__database,
                'guild_id': self.__guild_id,
                'emoji_name': self.__emoji_name
            }
        )

        return self

    def addval_file_type(self) -> EmojiValidator:
        """
        Add a validator to check if the Emoji file is valid type.
        Only the image file that supported by Discord are supported.

        The validator must have this property before validation. 
        - `attachment`: :class:`discord.Attachment` object to be uploaded as an Emoji.
        
        :class:`EmojiNotFoundError` will be raised if:
        - `attachment` is None.
        - The `attachment` is not valid file type.

        :return: self
        :rtype: EmojiValidator
        """
        def validate_file_type(attachment: Attachment):
            conditions = [
                attachment is None,
                attachment.content_type not in ALLOWED_FILETYPES
            ]

            if any(conditions):
                raise EmojiFileTypeError(
                    message='*.%s is invalid file type for Emoji.',
                    message_args=(attachment.content_type,)
                )

        self.__add_validator(
            validate_file_type,
            {
                'attachment': self.__attachment
            }
        )

        return self

    def addval_file_size(self, maxsize: int) -> EmojiValidator:
        """
        Add a validator to check if the Emoji file is smaller the size limit.

        The validator must have this property before validation. 
        - `attachment`: :class:`discord.Attachment` object to be uploaded as an Emoji.
        
        :class:`EmojiFileTooLargeError` will be raised if:
        - `attachment` is None.
        - The size of an `attachment` is larger than the `maxsize`.

        :param maxsize: Max size of the file in kilobyte(KB).
        :type maxsize: int

        :return: self
        :rtype: EmojiValidator
        """
        def validate_file_size(attachment: Attachment, maxsize: int):
            conditions = [
                attachment is None,
                attachment.size > maxsize*1024
            ]

            if any(conditions):
                raise EmojiFileTooLargeError(
                    message='Image file(%.2f KB) is larger than the size limit(%d KB).',
                    message_args=(attachment.size/1024, maxsize)
                )

        self.__add_validator(
            validate_file_size,
            {
                'attachment': self.__attachment,
                'maxsize': maxsize
            }
        )

        return self

    def addval_capacity_limit(self, capacity: int) -> EmojiValidator:
        """
        Add a validator to check if a number of the Emoji is smaller the capacity limit.
        If the `capacity` is -1, then the validation always be success.

        The validator must have this property before validation. 
        - `database`: Emoji database to search for.
        - `guild_id`: Id of the guild.
        
        :class:`EmojiCapacityExceededError` will be raised if:
        - `database` or `guild_id` is None.
        - The number of the Emoji in the guild is larger than the `capacity`.

        :param capacity: A capacity limit.
        :type capacity: int

        :return: self
        :rtype: EmojiValidator
        """
        def validate_capacity_limit(database: database.BaseEmojiDatabase,
                                    guild_id: int,
                                    capacity: int):
            if capacity == -1:
                return

            conditions = [
                None in (database, guild_id),
                database.count(guild_id=guild_id) >= capacity,
            ]

            if any(conditions):
                raise EmojiCapacityExceededError(
                    message='The capacity limit exceeded. (%d)',
                    message_args=(capacity)
                )

        self.__add_validator(
            validate_capacity_limit,
            {
                'database': self.__database,
                'guild_id': self.__guild_id,
                'capacity': capacity
            }
        )

        return self

    def validate(self):
        """
        Validate the data with assigned validators. 
        If no validator is assigned, it does nothing. 
        Validators will be called in the order of assignment.
        """

        for v in self.__validators:
            try:
                v['func'](**v['kwargs'])
            except EmojiError as e:
                raise e
