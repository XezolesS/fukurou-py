class EmojiUse:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def emoji_name(self) -> str:
        return self.__emoji_name

    @property
    def use_count(self) -> int:
        return self.__use_count

    def __init__(self,
                 guild_id: int,
                 emoji_name: str,
                 uploader_id: int,
                 use_count: int = 0) -> None:
        self.__guild_id = guild_id
        self.__emoji_name = emoji_name
        self.__user_id = uploader_id
        self.__use_count = use_count
