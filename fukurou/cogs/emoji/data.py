from __future__ import annotations
from datetime import datetime, timezone
from typing import Tuple

class Emoji:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def emoji_name(self) -> str:
        return self.__emoji_name

    @property
    def uploader_id(self) -> int:
        return self.__uploader_id

    @property
    def file_name(self) -> str:
        return self.__file_name

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    def __init__(self,
                 guild_id: int,
                 emoji_name: str,
                 uploader_id: int,
                 file_name: str,
                 created_at: datetime = datetime.now(timezone.utc)) -> None:
        self.__guild_id = guild_id
        self.__emoji_name = emoji_name
        self.__uploader_id = uploader_id
        self.__file_name = file_name
        self.__created_at = created_at

    @classmethod
    def from_entry(cls, entry: Tuple) -> Emoji | None:
        if not isinstance(entry, Tuple):
            return None

        try:
            return Emoji(
                guild_id=int(entry[0]),
                emoji_name=entry[1],
                uploader_id=int(entry[2]),
                file_name=entry[3],
                created_at=datetime.fromisoformat(entry[4])
            )
        except ValueError:
            return None
        except TypeError:
            return None

    def to_entry(self) -> Tuple:
        return (self.guild_id, self.emoji_name, self.uploader_id, self.file_name, self.created_at)

class EmojiListItem:
    @property
    def emoji_name(self) -> str:
        return self.__emoji_name

    @property
    def uploader_id(self) -> int:
        return self.__uploader_id

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def use_count(self) -> int:
        return self.__use_count

    def __init__(self, entry: Tuple) -> None:
        if not isinstance(entry, Tuple):
            return

        try:
            self.__emoji_name = entry[0]
            self.__uploader_id = int(entry[1])
            self.__created_at = datetime.fromisoformat(entry[2])
            self.__use_count = int(entry[3])
        except ValueError:
            return
        except TypeError:
            return

class EmojiList:
    def __init__(self, entries: list[Tuple]) -> None:
        self.__cur = -1
        self.__data = []

        for e in entries:
            self.__data.append(EmojiListItem(entry=e))

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return self

    def __next__(self) -> EmojiListItem:
        self.__cur += 1

        if self.__cur < len(self.__data):
            return self.__data[self.__cur]

        raise StopIteration

    def __getitem__(self, key) -> EmojiListItem:
        return self.__data[self.__cur]
