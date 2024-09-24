from abc import ABC, abstractmethod
from os import PathLike
import logging

from fukurou.cogs.emoji.config import EmojiConfig

class BaseEmojiStorage(ABC):
    """
    Abstract class for interacting with the Emoji storage.
    """
    def __init__(self, config: EmojiConfig) -> None:
        self.logger = logging.getLogger('fukurou.emoji.storage')
        self.config: EmojiConfig = config
        self._setup()

    @abstractmethod
    def _setup(self) -> None:
        """
        A method for setting up the storage connection. 
        This method will be called in `__init__()`.
        """
        raise NotImplementedError("BaseEmojiStorage._setup() is not implemented!")

    @abstractmethod
    def get_guild_loc(self, guild_id: int) -> str | PathLike:
        """
        Get guild's storage location.

        :param guild_id: Id of the guild.
        :type guild_id: int

        :return: Directory, URL or such path like string.
        :rtype: str | PathLike
        """
        raise NotImplementedError("BaseEmojiStorage.get_guild_loc() is not implemented!")

    @abstractmethod
    def register(self, guild_id: int) -> None:
        """
        A method for registering a guild to the storage. 
        Be aware, the method DOES NOT store guild's ID into the instance. 
        The method creates and validates guild specific storage for their Emojis.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        raise NotImplementedError("BaseEmojiStorage._register() is not implemented!")

    @abstractmethod
    def get(self, guild_id: int, file_name: str, **kwargs) -> str | PathLike:
        """
        Get Path/URL of the image.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param file_name: Name of the image file.
        :type file_name: str

        :return: Path or URL of the image.
        :rtype: str | PathLike
        """
        raise NotImplementedError("BaseEmojiStorage.get() is not implemented!")

    @abstractmethod
    def save(self, guild_id: int, file: bytes, file_name: str, **kwargs) -> None:
        """
        Save emoji image to the storage.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param file: Image file, in bytes.
        :type file: bytes
        :param file_name: Name of the file.
        :type file_name: str
        """
        raise NotImplementedError("BaseEmojiStorage.save() is not implemented!")

    @abstractmethod
    def delete(self, guild_id: int, file_name: str, **kwargs) -> None:
        """
        Delete the file from the storage.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param file_name: Name of the image file.
        :type file_name: str
        """
        raise NotImplementedError("BaseEmojiStorage.delete() is not implemented!")
    