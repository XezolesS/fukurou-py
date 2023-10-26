from abc import ABC, abstractmethod
from os import PathLike

class BaseEmojiStorage(ABC):
    """
    Abstract class for interacting with the Emoji storage. 
    Since Discord 
    """
    def __init__(self):
        self._setup()

    @abstractmethod
    def _setup(self):
        """
        A method for setting up the storage connection. 
        This method will be called when `__init__` is called.
        """
        raise NotImplementedError("BaseEmojiStorage._setup() is not implemented!")

    @abstractmethod
    def _register(self, guild_id: int):
        """
        A method for register a guild to the storage. 

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
    def save(self, guild_id: int, file: bytes, ext: str, **kwargs) -> None:
        """
        Save emoji image to the storage.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param file: Image file in bytes.
        :type file: bytes
        :param ext: Extension of the file.
        :type ext: str
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
