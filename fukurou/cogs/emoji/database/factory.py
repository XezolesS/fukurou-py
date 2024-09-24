from typing import TypeVar

from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.database.base import BaseEmojiDatabase
from fukurou.cogs.emoji.database.sqlite import EmojiSqlite

EmojiDatabase = TypeVar('EmojiDatabase', bound=BaseEmojiDatabase)

def get_emoji_database(config: EmojiConfig) -> EmojiDatabase:
    """
    Get a database connector for the Emoji.

    Parameters
    ----------
    config : EmojiConfig
        Config instance

    Returns
    -------
    EmojiDatabase
        Database instance built by the config

    Raises
    ------
    ValueError
        If database type is invalid
    """
    match config.database.type.lower():
        case 'sqlite':
            return EmojiSqlite(config)

    # TODO: Error logging?
    raise ValueError('There is no such database', config.database.type)
