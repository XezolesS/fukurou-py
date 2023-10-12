class TagMap:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def emoji_name(self) -> str:
        return self.__emoji_name

    @property
    def tag_name(self) -> str:
        return self.__tag_name

    def __init__(self, guild_id: int, emoji_name: str, tag_name: str):
        self.__guild_id = guild_id
        self.__emoji_name = emoji_name
        self.__tag_name = tag_name
