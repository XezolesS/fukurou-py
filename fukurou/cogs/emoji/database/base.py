from abc import ABC, abstractmethod
import logging

from fukurou.cogs.emoji.data import Emoji, EmojiList

class BaseEmojiDatabase(ABC):
    """
    Abstract class to communicate with the Emoji database.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger('fukurou.emoji.database')
        self._connect()
        self._init_tables()

    @abstractmethod
    def _connect(self) -> None:
        """
        Make a connection to the database. 
        This method will be called in `__init__()`.
        """
        raise NotImplementedError("BaseEmojiDatabase._connect() is not implemented!")

    @abstractmethod
    def _init_tables(self) -> None:
        """
        Create tables to the database.
        This method will be called in `__init__()`.
        """
        raise NotImplementedError("BaseEmojiDatabase._init_tables() is not implemented!")

    @abstractmethod
    def exists(self, guild_id: int, emoji_name: str) -> bool:
        """
        Check if the Emoji exists.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :return: True if it exists, False if there's no such.
        :rtype: bool
        """
        raise NotImplementedError("BaseEmojiDatabase.exists() is not implemented!")

    @abstractmethod
    def file_exists(self, guild_id: int, file_name: str) -> str | None:
        """
        Check if the Emoji file exists.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param file_name: Name of the Emoji.
        :type file_name: str

        :return: Name of the Emoji that is corresponds with the file, None if there is no such.
        :rtype: str | None
        """
        raise NotImplementedError("BaseEmojiDatabase.file_exists() is not implemented!")

    @abstractmethod
    def get(self, guild_id: int, emoji_name: str) -> Emoji | None:
        """
        Get Emoji object from `guild_id` and `emoji_name` within the database.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :return: Emoji object, None if there's no such.
        :rtype: Emoji | None
        """
        raise NotImplementedError("BaseEmojiDatabase.get() is not implemented!")

    @abstractmethod
    def add(self, guild_id: int, uploader_id: int, emoji_name: str, file_name: str) -> None:
        """
        Add Emoji data to the database.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        :param uploader_id: Id of the uploader.
        :type uploader_id: str
        :param file_name: Name of the file.
        :type file_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        raise NotImplementedError("BaseEmojiDatabase.add() is not implemented!")

    @abstractmethod
    def delete(self, guild_id: int, emoji_name: str) -> None:
        """
        Delete Emoji record from the database.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        raise NotImplementedError("BaseEmojiDatabase.delete() is not implemented!")

    @abstractmethod
    def rename(self, guild_id: int, old_name: str, new_name: str) -> None:
        """
        Rename a Emoji named `old_name` to `new_name` in the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param old_name: Old name of the Emoji.
        :type old_name: str
        :param new_name: New name of the Emoji.
        :type new_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        raise NotImplementedError("BaseEmojiDatabase.rename() is not implemented!")

    @abstractmethod
    def replace(self, guild_id: int, uploader_id: int, emoji_name: str, file_name: str) -> None:
        """
        Replace Emoji data in the database.

        :param guild_id: Id of the guild.
        :type guild_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str
        :param uploader_id: Id of the uploader.
        :type uploader_id: str
        :param file_name: Name of the file.
        :type file_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        raise NotImplementedError("BaseEmojiDatabase.replace() is not implemented!")

    @abstractmethod
    def list(self, user_id: int, guild_id: int, keyword: str = None) -> EmojiList:
        """
        Build a list of Emojis with its details in the guild. 
        It has details both for the user and the guild. 

        If `keyword` is given, it only stores the Emojis 
        which contain the kewyord in its name.

        :param user_id: Id of the user.
        :type user_id: int
        :param guild_id: Id of the guild.
        :type guild_id: int
        :param keyword: Keyword to search for.
        :type keyword: str, optional

        :return: List of the Emojis.
        :rtype: EmojiList
        """
        raise NotImplementedError("BaseEmojiDatabase.list() is not implemented!")

    @abstractmethod
    def count(self, guild_id: int) -> int:
        """
        Get the number of Emojis in the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int

        :return: Number of Emojis in the guild.
        :rtype: int
        """
        raise NotImplementedError("BaseEmojiDatabase.count() is not implemented!")

    @abstractmethod
    def increase_usecount(self, guild_id: int, user_id: int, emoji_name: str) -> None:
        """
        Increase an Emoji use count for the user in the guild.

        :param guild_id: Id of the Guild.
        :type guild_id: int
        :param user_id: Id of the user who used the Emoji.
        :type user_id: int
        :param emoji_name: Name of the Emoji.
        :type emoji_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        raise NotImplementedError("BaseEmojiDatabase.increase_usecount() is not implemented!")
