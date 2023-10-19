from __future__ import annotations
import os
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
    def file_path(self) -> str:
        return self.__file_path

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def file_name(self) -> str:
        return os.path.basename(self.__file_path)

    def __init__(self,
                 guild_id: int,
                 emoji_name: str,
                 uploader_id: int,
                 file_path: str,
                 created_at: datetime = datetime.now(timezone.utc)):
        self.__guild_id = guild_id
        self.__emoji_name = emoji_name
        self.__uploader_id = uploader_id
        self.__file_path = file_path
        self.__created_at = created_at

    @classmethod
    def from_entry(cls, entry: Tuple) -> Emoji:
        return Emoji(
            guild_id=int(entry[0]),
            emoji_name=entry[1],
            uploader_id=int(entry[2]),
            file_path=entry[3],
            created_at=datetime.fromisoformat(entry[4])
        )

    def to_entry(self) -> Tuple:
        return (self.guild_id, self.emoji_name, self.uploader_id, self.file_path, self.created_at)
