import os
import sqlite3
from datetime import datetime, timezone

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.patterns import Singleton
from fukurou.cogs.emoji.data import (
    Emoji,
    Tag,
    TagMap,
    TagRelation
)
from fukurou.cogs.emoji.exceptions import EmojiDatabaseError

class EmojiSqlite(metaclass=Singleton):
    TABLE_SCRIPT_PATH = './fukurou/cogs/emoji/database/script/sqlite_table_init.sql'
    WILDCARDS = {
        '%': r'\%',
        '_': r'\_',
        '\\': r'\\'
    }

    def __init__(self):
        self.__db_path = configs.get_config('emoji').database_fullpath
        self.__connect()
        self.__init_tables()

    def __connect(self):
        # Make directory first
        os.makedirs(configs.get_config('emoji').database_dir, exist_ok=True)

        self.__connection = sqlite3.connect(self.__db_path)
        self.__cursor = self.__connection.cursor()

    def __init_tables(self):
        logger.info('Initialize emoji database.')

        try:
            with open(self.TABLE_SCRIPT_PATH, 'r', encoding='utf8') as file:
                script = ''.join(file.readlines())
                self.__cursor.executescript(script)
        except IOError as e:
            logger.error('Error occured while reading initialization script for emoji databse: %s',
                         e.strerror)

            return
        except sqlite3.DatabaseError as e:
            logger.error('Error occured while executing script for emoji databse: %s',
                         e.args)

            return

        logger.info('Successfully initialize emoji database.')

    def save_emoji(self, guild_id: int, emoji_name: str, uploader_id: str, file_path: str):
        """
        Save emoji data to the database.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str
        :param uploader_id: Id of the emoji uploader.
        :type uploader_id: str
        :param file_path: Path of the emoji file.
        :type file_path: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        query = 'INSERT INTO emoji VALUES (?, ?, ?, ?, ?)'

        emoji = Emoji(
            guild_id=guild_id,
            emoji_name=emoji_name,
            uploader_id=uploader_id,
            file_path=file_path
        )

        try:
            self.__cursor.execute(query, emoji.to_entry())
        except sqlite3.Error as e:
            self.__connection.rollback()
            raise EmojiDatabaseError() from e

        self.__connection.commit()

    def delete_emoji(self, guild_id: int, emoji_name: str) -> bool:
        """
        Delete emoji record from the database.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str

        :raises EmojiDatabaseError: If database operation failed.

        :return: True if a record deleted, False if not.
        :rtype: bool
        """
        param_emoji_name = 'emoji_name'
        if configs.get_config('emoji').ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            emoji_name = emoji_name.replace(' ', '')

        query = f'DELETE FROM emoji WHERE guild_id=? AND {param_emoji_name}=?'

        try:
            self.__cursor.execute(query, (guild_id, emoji_name))
        except sqlite3.Error as e:
            self.__connection.rollback()
            raise EmojiDatabaseError() from e

        self.__connection.commit()

        # No deleted row.
        if self.__cursor.rowcount == 0:
            return False

        return True

    def get_emoji(self, guild_id: int, emoji_name: str) -> Emoji | None:
        """
        Get emoji data which matches with the `guild_id` and `emoji_name` from the database.

        :param guild_id: Guild Id of the emoji to search.
        :type guild_id: int
        :param emoji_name: Name of the emoji to search.
        :type emoji_name: str

        :return: Emoji object, None if there's no match.
        :rtype: Emoji | None
        """
        param_emoji_name = 'emoji_name'
        if configs.get_config('emoji').ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            emoji_name = emoji_name.replace(' ', '')

        query = f'SELECT * FROM emoji WHERE guild_id=? AND {param_emoji_name}=?'

        result = self.__cursor.execute(query, (guild_id, emoji_name))
        data = result.fetchone()

        if data is None:
            return None

        return Emoji.from_entry(data)

    def emoji_exists(self, guild_id: int, emoji_name: str) -> bool:
        """
        Check if emoji with a name exists.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str

        :return: True if it exists, False if not.
        :rtype: bool
        """
        return self.get_emoji(guild_id=guild_id, emoji_name=emoji_name) is not None

    def update_emoji_name(self, guild_id: int, old_name: str, new_name: str) -> bool:
        """
        Rename a emoji which has a name of 'old_name' to 'new_name' of the guild.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param old_name: Old name of the emoji.
        :type old_name: str
        :param new_name: New name of the emoji.
        :type new_name: str

        :raises EmojiDatabaseError: If database operation failed.

        :return: True if success, False if not.
        :rtype: bool
        """
        param_emoji_name = 'emoji_name'
        if configs.get_config('emoji').ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            old_name = old_name.replace(' ', '')

        query = f'UPDATE emoji SET emoji_name=? WHERE guild_id=? AND {param_emoji_name}=?'

        try:
            self.__cursor.execute(query, (new_name, guild_id, old_name))
        except sqlite3.Error as e:
            self.__connection.rollback()
            raise EmojiDatabaseError() from e

        self.__connection.commit()

        # No updated row.
        if self.__cursor.rowcount == 0:
            return False

        return True

    def emoji_list(self, guild_id: int, keyword: str = None) -> list[Emoji]:
        """
        Retrieve list of emojis of the guild. 
        If keyword is given, search for the emojis which contain the keyword in its name.

        :param guild_id: Guild Id to search.
        :type guild_id: int
        :param keyword: Keyword to search for.
        :type keyword: str

        :return: List of Emoji objects.
        :rtype: list[Emoji]
        """
        query = 'SELECT * FROM emoji WHERE guild_id=? '
        param = (guild_id,)

        if keyword is not None:
            # Escape wildcards
            for key, value in self.WILDCARDS.items():
                keyword = keyword.replace(key, value)

            keyword = f'%{keyword}%'

            query += r"AND emoji_name LIKE ? ESCAPE '\' "
            param += (keyword,)

        query += 'ORDER BY emoji_name;'

        logger.debug('Query: "%s"', query)

        result = self.__cursor.execute(query, param)
        data = result.fetchall()

        emoji_list = []
        for t in data:
            emoji_list.append(Emoji.from_entry(t))

        return emoji_list

    def increase_emoji_usecount(self, guild_id: int, user_id: int, emoji_name: str):
        """
        Increase an emoji use count for the user.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param user_id: User Id who used the emoji.
        :type user_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        # Check emoji usecount record exists or not
        query_exist_check = """
            SELECT * FROM emoji_use WHERE guild_id=? AND user_id=? AND emoji_name=?;
        """
        param = (guild_id, user_id, emoji_name)

        result_exist_check = self.__cursor.execute(query_exist_check, param)
        exists = result_exist_check.fetchone() is not None

        # Increase use count, create a record if it's not exist
        try:
            if exists is None:
                query = """
                    INSERT INTO emoji_use VALUES (?, ?, ?, ?);
                """
                param += (1,)
                self.__cursor.execute(query, param)
            else:
                query = """
                    UPDATE emoji_use SET use_count=use_count + 1
                    WHERE guild_id=? AND user_id=? AND emoji_name=?;
                """
                self.__cursor.execute(query, param)
        except sqlite3.Error as e:
            self.__connection.rollback()
            raise EmojiDatabaseError() from e

        self.__connection.commit()
            