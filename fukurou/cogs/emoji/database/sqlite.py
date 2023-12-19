import os
from contextlib import closing
import sqlite3

from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.data import Emoji, EmojiList
from fukurou.cogs.emoji.exceptions import EmojiDatabaseError
from .base import BaseEmojiDatabase

WILDCARDS = {
    '%': r'\%',
    '_': r'\_',
    '\\': r'\\'
}

class EmojiSqlite(BaseEmojiDatabase):
    def _connect(self):
        db_path = EmojiConfig().database.path
        db_dir = os.path.dirname(db_path)

        try:
            os.makedirs(name=db_dir, exist_ok=True)
            open(db_path, mode='x', encoding='utf8')
        except FileExistsError:
            self.logger.info('Successfully found database file for Emoji.')
        except OSError as e:
            self.logger.error('Cannot create database file: %s', e.strerror)
            return

        self.conn = sqlite3.connect(database=db_path)
        self.conn.execute('PRAGMA FOREIGN_KEYS = ON')

        self.logger.info('Connected to the Emoji database.')

    def _init_tables(self):
        script_relpath = os.path.join('script',  'sqlite_table_init.sql')
        script_path = os.path.join(os.path.dirname(__file__), script_relpath)
        self.logger.debug('Emoji table initialization script found at: %s', script_path)

        try:
            with open(script_path, 'r', encoding='utf8') as file:
                script = ''.join(file.readlines())

            with closing(self.conn.cursor()) as cursor:
                cursor.executescript(script)
        except IOError as e:
            self.logger.error('Error occured while reading initialization script for Emoji databse: %s',
                              e.strerror)
        except sqlite3.DatabaseError as e:
            self.logger.error('Error occured while executing script for Emoji databse: %s',
                              e.args)
        else:
            self.logger.info('Successfully initialized Emoji database.')

    def get(self, guild_id: int, emoji_name: str) -> Emoji | None:
        param_emoji_name = 'emoji_name'
        if EmojiConfig().expression.ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            emoji_name = emoji_name.replace(' ', '')

        query = f'SELECT * FROM emoji WHERE guild_id=? AND {param_emoji_name}=?'

        with closing(self.conn.cursor()) as cursor:
            result = cursor.execute(query, (guild_id, emoji_name))
            data = result.fetchone()

        return Emoji.from_entry(entry=data)

    def add(self, guild_id: int, uploader_id: int, emoji_name: str, file_name: str):
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
        param_emoji_name = 'emoji_name'
        if EmojiConfig().expression.ignore_spaces is True:
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
        param_emoji_name = 'emoji_name'
        if EmojiConfig().expression.ignore_spaces is True:
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

    def replace(self, guild_id: int, uploader_id: int, emoji_name: str, file_name: str) -> None:
        param_emoji_name = 'emoji_name'
        if EmojiConfig().expression.ignore_spaces is True:
            param_emoji_name = "replace(emoji_name, ' ', '')"
            emoji_name = emoji_name.replace(' ', '')

        query = f"""
            UPDATE emoji SET uploader_id=?, file_name=? 
            WHERE guild_id=? AND {param_emoji_name}=?"""

        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, (uploader_id, file_name, guild_id, emoji_name))
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()

    def list(self, user_id: int, guild_id: int, keyword: str = None) -> EmojiList:
        param = (user_id, guild_id,)

        keyword_clause = ''
        if keyword is not None:
            # Escape wildcards
            for key, value in WILDCARDS.items():
                keyword = keyword.replace(key, value)

            keyword = f'%{keyword}%'

            keyword_clause = r"AND e.emoji_name LIKE ? ESCAPE '\'"
            param += (keyword,)

        query = f"""
            SELECT
                e.emoji_name,
                e.uploader_id,
                e.created_at,
                COALESCE(
                    CASE 
                        WHEN u.user_id=? THEN u.use_count ELSE 0 
                    END, 0
                ) AS user_use_count,
                COALESCE(SUM(u.use_count), 0) AS use_count
            FROM emoji AS e
            LEFT OUTER JOIN emoji_use AS u
                ON e.guild_id=u.guild_id AND e.emoji_name=u.emoji_name
            WHERE e.guild_id=? {keyword_clause}
            GROUP BY e.emoji_name
            ORDER BY e.emoji_name ASC, use_count DESC, e.created_at ASC;
        """

        self.logger.debug('EmojiSqlite.list() query built: %s', query)

        with closing(self.conn.cursor()) as cursor:
            result = cursor.execute(query, param)
            data = result.fetchall()

        return EmojiList(owner_id=user_id, entries=data)

    def count(self, guild_id: int) -> int:
        query = 'SELECT COUNT(1) FROM emoji WHERE guild_id=?;'

        with closing(self.conn.cursor()) as cursor:
            result = cursor.execute(query, (guild_id,))
            count = int(result.fetchone()[0])

        return count

    def increase_usecount(self, guild_id: int, user_id: int, emoji_name: str) -> None:
        subquery_emoji_name = '?'
        if EmojiConfig().expression.ignore_spaces is True:
            subquery_emoji_name = """(
                SELECT emoji_name FROM emoji WHERE replace(emoji_name, ' ', '')=?
            )"""
            emoji_name = emoji_name.replace(' ', '')

        query = f"""
            INSERT OR IGNORE INTO emoji_use VALUES (?, ?, {subquery_emoji_name}, ?)
            ON CONFLICT(guild_id, user_id, emoji_name)
            DO UPDATE SET use_count=use_count + 1;
        """

        self.logger.debug('EmojiSqlite.increase_usecount() query built: %s', query)

        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, (guild_id, user_id, emoji_name, 1))
        except sqlite3.Error as e:
            self.conn.rollback()
            raise EmojiDatabaseError() from e

        self.conn.commit()
