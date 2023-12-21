from .base import BaseEmojiDatabase
from .sqlite import EmojiSqlite

def get_emoji_database(dbtype: str) -> BaseEmojiDatabase:
    """
    Get a database connector for the Emoji.

    :param dbtype: Type of the database in string.
    :type dbtype: str

    :return: Database connector.
    :rtype: BaseEmojiDatabase

    :raises ValueError: If the `dbtype` is invalid database.
    """
    match dbtype:
        case 'sqlite':
            return EmojiSqlite()

    raise ValueError('There is no such database', dbtype)
