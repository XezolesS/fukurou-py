from datetime import datetime

class Emoji:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def uploader_id(self) -> int:
        return self.__uploader_id

    @property
    def path(self) -> str:
        return self.__path

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def use_count(self) -> int:
        return self.__use_count

    def __init__(self,
                 guild_id: int,
                 name: str,
                 uploader_id: int,
                 path: str,
                 created_at: datetime = datetime.now(),
                 use_count: int = 0):
        self.__guild_id = guild_id
        self.__name = name
        self.__uploader_id = uploader_id
        self.__path = path
        self.__created_at = created_at
        self.__use_count = use_count
