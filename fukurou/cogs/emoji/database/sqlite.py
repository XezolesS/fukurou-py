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
    TABLE_EMOJI = 'emoji'
    TABLE_TAG = 'tag'
    TABLE_TAGMAP = 'tagmap'
    TABLE_TAG_RELATION = 'tag_relation'

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
        self.__create_emoji_table()
        self.__create_tag_table()
        self.__create_tagmap_table()
        self.__create_tag_relation_table()

    def __create_emoji_table(self):
        logger.info('Initializing table %s in %s', self.TABLE_EMOJI, self.__db_path)
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_EMOJI} (
            guild_id INTEGER,
            name TEXT,
            uploader_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            created_at DATETIME,
            use_count INT,
            PRIMARY KEY (guild_id, name)
        );
        """

        self.__cursor.execute(query)

    def __create_tag_table(self):
        logger.info('Initializing table %s in %s', self.TABLE_TAG, self.__db_path)
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_TAG} (
            guild_id INTEGER,
            name TEXT,
            PRIMARY KEY (guild_id, name)
        );
        """

        self.__cursor.execute(query)

    def __create_tagmap_table(self):
        logger.info('Initializing table %s in %s', self.TABLE_TAGMAP, self.__db_path)
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_TAGMAP} (
            guild_id INTEGER,
            emoji_name TEXT,
            tag_name TEXT,
            FOREIGN KEY (guild_id) REFERENCES tag(guild_id),
            FOREIGN KEY (emoji_name) REFERENCES emoji(name),
            FOREIGN KEY (tag_name) REFERENCES tag(name)
        );
        """

        self.__cursor.execute(query)

    def __create_tag_relation_table(self):
        logger.info('Initializing table %s in %s', self.TABLE_TAG_RELATION, self.__db_path)
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_TAG_RELATION} (
            guild_id INTEGER,
            tag_name TEXT,
            parent_name TEXT,
            FOREIGN KEY (guild_id) REFERENCES tag(guild_id),
            FOREIGN KEY (tag_name) REFERENCES tag(name),
            FOREIGN KEY (parent_name) REFERENCES tag(name)
        );
        """

        self.__cursor.execute(query)

    def save_emoji(self, guild_id: int, name: str, uploader: str, path: str):
        """
        Save emoji data to the database.

        :param int guild_id: Guild Id of the emoji.
        :param str name: Name of the emoji.
        :param str uploader: Id of the emoji uploader.
        :param str path: File path of the emoji.
        """
        query = f"""
            INSERT INTO {self.TABLE_EMOJI} VALUES (?, ?, ?, ?, ?, ?)
        """

        entry = (
            guild_id,
            name,
            uploader,
            path,
            datetime.now(timezone.utc),
            0
        )

        try:
            self.__cursor.execute(query, entry)
            self.__connection.commit()
        except sqlite3.Error as e:
            raise EmojiDatabaseError() from e

    def get_emoji(self, guild_id: int, name: str) -> Emoji | None:
        """
        Get emoji data which matches with the `guild_id` and `name` from the database.

        :param int guild_id: Guild Id of the emoji to search.
        :param str name: Name of the emoji to search.

        :return: Emoji object, None if there's no match.
        :rtype: Emoji | None
        """
        query = f"""
            SELECT * FROM {self.TABLE_EMOJI} WHERE guild_id=? AND name=?
        """

        result = self.__cursor.execute(query, (guild_id, name))
        data = result.fetchone()

        if data is None:
            return None

        return Emoji(
            guild_id=data[0],
            name=data[1],
            uploader_id=data[2],
            path=data[3],
            created_at=data[4],
            use_count=data[5]
        )

    def emoji_exists(self, guild_id: int, name: str) -> bool:
        """
        Check if emoji with a name exists.

        :param int guild_id: Guild Id of the emoji.
        :param str name: Name of the emoji.

        :return: True if it exists, False if not.
        :rtype: bool
        """
        return self.get_emoji(guild_id=guild_id, name=name) is not None

    def update_emoji_name(self, guild_id: int, old_name: str, new_name: str) -> bool:
        """
        Rename a emoji which has a name of 'old_name' to 'new_name' of the guild.

        :param guild_id: Guild Id of the emoji.
        :type guild_id: int
        :param old_name: Old name of the emoji.
        :type old_name: str
        :param new_name: New name of the emoji.
        :type new_name: str

        :return: True if success, False if not.
        :rtype: bool
        """
        query = f"""
            UPDATE {self.TABLE_EMOJI} SET name=? WHERE guild_id=? AND name=?
        """

        self.__cursor.execute(query, (new_name, guild_id, old_name))
        logger.debug('update_emoji_name() -> rowcount: %d', self.__cursor.rowcount)

        # Update failed.
        if self.__cursor.rowcount == 0:
            return False

        self.__connection.commit()

        return True
