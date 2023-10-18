class Tag:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def name(self) -> str:
        return self.__tag_name

    def __init__(self, guild_id: int, tag_name: str):
        self.__guild_id = guild_id
        self.__tag_name = tag_name
