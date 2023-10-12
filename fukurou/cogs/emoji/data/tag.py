class Tag:
    @property
    def guild_id(self) -> int:
        return self.__guild_id

    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, guild_id: int, name: str):
        self.__guild_id = guild_id
        self.__name = name
