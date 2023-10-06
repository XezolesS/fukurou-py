import os

from fukurou.configs import configs
from fukurou.logging import logger
from fukurou.cogs.emoji.config import EmojiConfig

class ImageHandler:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.config: EmojiConfig = configs.get_config('emoji')

        self.__init_local_directory()

    def save_image(self, name: str):
        pass

    def get_image(self, path: str):
        pass

    def __init_local_directory(self):
        logger.debug('Image storage type is %s', self.config.storage_type)
        if self.config.storage_type != 'local':
            return

        abs_path = os.path.abspath(self.config.storage_dir)
        logger.debug('Root image path is %s', abs_path)
        if not os.path.exists(abs_path):
            os.mkdir(abs_path)
            logger.info('Root image directory created at: %s', abs_path)

        guild_path = os.path.join(abs_path, str(self.guild_id))
        if not os.path.exists(guild_path):
            os.mkdir(guild_path)
