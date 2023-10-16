import os

from fukurou.configs import BaseConfig, add_config

class EmojiConfig(BaseConfig):
    @property
    def name(self) -> str:
        return 'emoji'

    @property
    def keys(self) -> list[str]:
        return [
            'database',
            'storage'
        ]

    @property
    def default_values(self) -> dict[str, any]:
        return {
            'database': {
                'type': 'sqlite',
                'file': 'emoji.db',
                'directory': './databases'
            },
            'storage': {
                'type': 'local',
                'directory': './images'
            }
        }

    @property
    def database_type(self) -> str:
        return self.get_value('database')['type']

    @property
    def database_file(self) -> str:
        return self.get_value('database')['file']

    @property
    def database_dir(self) -> str:
        return self.get_value('database')['directory']

    @property
    def database_fullpath(self) -> str:
        return os.path.abspath(os.path.join(self.database_dir, self.database_file))

    @property
    def storage_type(self) -> str:
        return self.get_value('storage')['type']

    @property
    def storage_dir(self) -> str:
        return self.get_value('storage')['directory']

add_config(EmojiConfig())
