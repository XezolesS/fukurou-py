from abc import ABC, abstractmethod

from fukurou.cogs.emoji.data import Emoji

class BaseEmojiDatabase(ABC):
    """
    Abstract class to communicate with the Emoji database.
    This class is Singleton.
    """
    def __init__(self) -> None:
        self._connect()
        self._init_tables()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("BaseEmojiDatabase._connect() is not implemented!")

    @abstractmethod
    def _init_tables(self) -> None:
        raise NotImplementedError("BaseEmojiDatabase._init_tables() is not implemented!")

    @abstractmethod
    def get(self, guild_id: int, emoji_name: str) -> Emoji | None:
        raise NotImplementedError("BaseEmojiDatabase.get() is not implemented!")

    @abstractmethod
    def exists(self, guild_id: int, emoji_name: str) -> bool:
        raise NotImplementedError("BaseEmojiDatabase.exists() is not implemented!")

    @abstractmethod
    def add(self, guild_id: int, emoji_name: str, uploader_id: str, file_name: str) -> None:
        raise NotImplementedError("BaseEmojiDatabase.add() is not implemented!")

    @abstractmethod
    def delete(self, guild_id: int, emoji_name: str) -> bool:
        raise NotImplementedError("BaseEmojiDatabase.delete() is not implemented!")

    @abstractmethod
    def rename(self, guild_id: int, old_name: str, new_name: str) -> bool:
        raise NotImplementedError("BaseEmojiDatabase.rename() is not implemented!")

    @abstractmethod
    def list(self, guild_id: int, keyword: str = None) -> list[Emoji]:
        raise NotImplementedError("BaseEmojiDatabase.list() is not implemented!")

    @abstractmethod
    def increase_usecount(self, guild_id: int, user_id: int, emoji_name: str)  -> None:
        raise NotImplementedError("BaseEmojiDatabase.increase_usecount() is not implemented!")
