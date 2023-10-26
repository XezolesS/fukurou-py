from typing import Final

from fukurou.patterns import Singleton

ALLOWED_FILETYPES: Final = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
}

class GuildEmojiManager:
    def __init__(self, guild_id: int) -> None:
        self.guild_id = guild_id

class EmojiManager(metaclass=Singleton):
    """
    A class for mapping GuildEmojiManager with the guild ID. 
    This class will create only one instance.
    """
    __managers: dict[str, GuildEmojiManager] = {}

    def __getitem__(self, key: str) -> GuildEmojiManager:
        return self.__managers[key]

    def __setitem__(self, key: str, value: GuildEmojiManager) -> None:
        self.__managers[key] = value

    def add_manager(self, guild_id: int) -> None:
        """
        Add a GuildEmojiManager for the guild.

        :param guild_id: Id of the guild.
        :type guild_id: int
        """
        self.__managers[guild_id] = GuildEmojiManager(guild_id=guild_id)

    def add_managers(self, guild_ids: list[int]) -> None:
        """
        Add list of GuildEmojiManager for each guilds.

        :param guild_ids: List of guild Id.
        :type guild_ids: list[int]
        """
        for guild_id in guild_ids:
            self.__managers[guild_id] = GuildEmojiManager(guild_id=guild_id)
