import hashlib
import os
import re
from typing import TypedDict
import requests

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.exceptions import (
    EmojiNameExistsError,
    EmojiDatabaseError,
    EmojiFileExistsError,
    EmojiFileSaveError,
    EmojiFileTypeError,
    EmojiInvalidNameError
)
from fukurou.cogs.emoji.data import Emoji
from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.database import sqlite

class ImageHandler:
    ALLOWED_FILETYPES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/bmp',
    }

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

    def __verify_filetype(self, file_type: str) -> str | None:
        return file_type.removeprefix('image/') if file_type in self.ALLOWED_FILETYPES else None

    def __save_local_image(self, file_url: str, ext: str) -> str:
        # Download file from url
        try:
            response = requests.get(url=file_url, stream=True, timeout=10)
            response.raise_for_status()

            image = response.content
        except requests.exceptions.HTTPError as e:
            raise EmojiFileSaveError(e.args) from e
        except requests.exceptions.RequestException as e:
            raise EmojiFileSaveError(e.args) from e

        # Build md5 checksum of a file
        checksum = hashlib.md5(image).hexdigest()
        file_name = f'{checksum}.{ext}'

        # Check if file already exists
        path = os.path.join(self.directory, file_name)
        if os.path.exists(path):
            raise EmojiFileExistsError(file_name=file_name, directory=self.directory)

        # Save a file to the local storage
        try:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

        except OSError as e:
            raise EmojiFileSaveError(e.args) from e

        return path

    def __delete_local_image(self, path: str):
        if os.path.exists(path=path):
            os.remove(path=path)

    def save_emoji(self, name: str, uploader: int, file_url: str, file_type: str) -> None:
        """
        Saves emoji with a given data.

        :param name: Name of the emoji.
        :type name: str
        :param uploader: Id of the uploader.
        :type uploader: int
        :param file_url: URL of the image file.
        :type file_url: str
        :param file_type: Type of the file represented as MIME.
        :type file_type: str

        :raises EmojiInvalidNameError: If name is not match with the pattern from config.
        :raises EmojiDuplicateNameError: If given name is already exist in the database.
        :raises EmojiFileTypeError: If file type is not supported.
        :raises EmojiFileExistsError: If image file is already exist.
        :raises EmojiFileSaveError: If an error occured while saving image file.
        :raises EmojiDatabaseError: If an error occured while saving emoji data to the database.
        """
        logger.info("User(%d) uploading emoji: (Name: %s, FileUrl: %s, FileType: %s)",
                    uploader,
                    name,
                    file_url,
                    file_type)

        # Check name validity
        pattern = f'^{self.config.expression_pattern}$'
        if not re.match(pattern=pattern, string=name):
            raise EmojiInvalidNameError(
                message='Name %s is not matched with the pattern.',
                message_args=(name,)
            )

        # Check for duplicate name
        database = sqlite.EmojiSqlite()
        emoji = database.get_emoji(guild_id=self.guild_id, name=name)
        if emoji is not None:
            raise EmojiNameExistsError(
                message='Emoji %s is already exist.',
                message_args=(name,)
            )

        # Check if the file is image
        ext = self.__verify_filetype(file_type=file_type)
        if ext is None:
            raise EmojiFileTypeError(
                message='*.%s is invalid file type for Emoji.',
                message_args=(ext,)
            )

        # Save image to the storage
        try:
            path = str()
            match self.config.storage_type:
                case 'local':
                    path = self.__save_local_image(file_url=file_url, ext=ext)
        except EmojiFileExistsError as e:
            raise EmojiFileExistsError(
                message='Image %s is already exist in %s',
                message_args=(e.file_name, e.directory)
            ) from e
        except EmojiFileSaveError as e:
            raise EmojiFileSaveError(
                message='Error occured while downloading file: %s',
                message_args=(e.args,)
            ) from e

        # Save emoji data to the database
        try:
            database.save_emoji(guild_id=self.guild_id,
                                name=name,
                                uploader=uploader,
                                path=path)
        except EmojiDatabaseError as e:
            self.__delete_local_image(path=path)

            raise EmojiDatabaseError(
                message='Error occured while saving emoji data: %s',
                message_args=(e.args,)
            ) from e

        logger.info('Emoji "%s" is saved at "%s"', name, path)

    def get_emoji(self, name: str) -> Emoji | None:
        """
        Get emoji data which matches with the `name`.

        :param name: Name of the emoji.
        :type name: str

        :return: `Emoji` object, `None` if there's no match.
        :rtype: Emoji | None
        """
        database = sqlite.EmojiSqlite()
        return database.get_emoji(guild_id=self.guild_id, name=name)

    def rename_emoji(self, old_name: str, new_name: str):
        """
        Rename emoji with a `old_name` to `new_name`.

        :param old_name: Old name of the emoji.
        :type old_name: str
        :param new_name: New name of the emoji.
        :type new_name: str

        :return: 
        :rtype: 
        """
        database = sqlite.EmojiSqlite()
        return database.update_emoji_name(guild_id=self.guild_id,
                                          old_name=old_name,
                                          new_name=new_name)

class ImageHandlers(TypedDict):
    guild_id: int
    handler: ImageHandler
