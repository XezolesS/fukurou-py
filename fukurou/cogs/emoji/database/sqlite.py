import os
from contextlib import closing
import sqlite3

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.data import Emoji
from fukurou.cogs.emoji.exceptions import EmojiDatabaseError
from .base import BaseEmojiDatabase

class EmojiSqlite(BaseEmojiDatabase):
    TABLE_SCRIPT_PATH = './fukurou/cogs/emoji/database/script/sqlite_table_init.sql'
    WILDCARDS = {
        '%': r'\%',
        '_': r'\_',
        '\\': r'\\'
    }

    def _connect(self):
        db_path = configs.get_config('emoji').database_fullpath

        try:
            if not os.path.exists(db_path):
               os.makedirs(name=db_path, exist_ok=True)
        except OSError as e:
            logger.error('Cannot create database file: %s', e.strerror)
        else:
            self.conn = sqlite3.connect(database=db_path)
            self.conn.execute('PRAGMA FOREIGN_KEYS = ON')

            logger.info('Connected to the Emoji database.')

    def _init_tables(self):
        script_relpath = os.path.join('script',  'sqlite_table_init.sql')
        script_path = os.path.join(os.path.dirname(__file__), script_relpath)
        logger.debug('Emoji table initialization script found at: %s', script_path)

        try:
            with open(script_path, 'r', encoding='utf8') as file:
                script = ''.join(file.readlines())

            with closing(self.conn.cursor()) as cursor:
                cursor.executescript(script)
        except IOError as e:
            logger.error('Error occured while reading initialization script for Emoji databse: %s',
                         e.strerror)
        except sqlite3.DatabaseError as e:
            logger.error('Error occured while executing script for Emoji databse: %s',
                         e.args)
        else:
            logger.info('Successfully initialized Emoji database.')

    def get(self, guild_id: int, emoji_name: str) -> Emoji | None:
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

        with closing(self.conn.cursor()) as cursor:
            result = cursor.execute(query, (guild_id, emoji_name))
            data = result.fetchone()

        return Emoji.from_entry(entry=data)

    def exists(self, guild_id: int, emoji_name: str) -> bool:
        """
        Check if emoji with a name exists.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str

        :return: True if it exists, False if not.
        :rtype: bool
        """
        return self.get(guild_id=guild_id, emoji_name=emoji_name) is not None

    def add(self, guild_id: int, emoji_name: str, uploader_id: str, file_name: str):
        """
        Add emoji data to the database.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str
        :param uploader_id: Id of the emoji uploader.
        :type uploader_id: str
        :param file_name: Name of the emoji file.
        :type file_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        query = 'INSERT INTO emoji VALUES (?, ?, ?, ?, ?)'

        emoji = Emoji(
            guild_id=guild_id,
            emoji_name=emoji_name,
            uploader_id=uploader_id,
            file_name=file_name
        )

        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, emoji.to_entry())
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()

    def delete(self, guild_id: int, emoji_name: str) -> None:
        """
        Delete emoji record from the database.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param emoji_name: Name of the emoji.
        :type emoji_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        param_emoji_name = 'emoji_name'
        if configs.get_config('emoji').ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            emoji_name = emoji_name.replace(' ', '')

        query = f'DELETE FROM emoji WHERE guild_id=? AND {param_emoji_name}=?'

        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, (guild_id, emoji_name))
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()

    def rename(self, guild_id: int, old_name: str, new_name: str) -> None:
        """
        Rename a emoji which has a name of 'old_name' to 'new_name' of the guild.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param old_name: Old name of the emoji.
        :type old_name: str
        :param new_name: New name of the emoji.
        :type new_name: str

        :raises EmojiDatabaseError: If database operation failed.
        """
        param_emoji_name = 'emoji_name'
        if configs.get_config('emoji').ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            old_name = old_name.replace(' ', '')

        query = f'UPDATE emoji SET emoji_name=? WHERE guild_id=? AND {param_emoji_name}=?'

        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, (new_name, guild_id, old_name))
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()

    def list(self, guild_id: int, keyword: str = None) -> list[Emoji]:
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

        with closing(self.conn.cursor()) as cursor:
            result = cursor.execute(query, param)
            data = result.fetchall()

        emoji_list = []
        for t in data:
            emoji_list.append(Emoji.from_entry(t))

        return emoji_list

    def increase_usecount(self, guild_id: int, user_id: int, emoji_name: str) -> None:
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
        try:
            # Increase use count, create a record if it's not exist
            with closing(self.conn.cursor()) as cursor:
                query = """
                    INSERT OR IGNORE INTO emoji_use VALUES (?, ?, ?, ?);
                """
                cursor.execute(query, (guild_id, user_id, emoji_name, 0))

                query = """
                    UPDATE emoji_use SET use_count=use_count + 1
                    WHERE guild_id=? AND user_id=? AND emoji_name=?;
                """
                cursor.execute(query, (guild_id, user_id, emoji_name))
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()
