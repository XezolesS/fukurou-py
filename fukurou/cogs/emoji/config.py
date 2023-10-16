import os

from fukurou.configs import BaseConfig, add_config
from fukurou.logging import logger

class EmojiConfig(BaseConfig):
    @property
    def name(self) -> str:
        return 'emoji'

    @property
    def keys(self) -> list[str]:
        return [
            'expression'
            'database',
            'storage'
        ]

    @property
    def default_values(self) -> dict[str, any]:
        return {
            'expression': {
                'pattern': '[a-zA-Z0-9_ -]+',
                'opening': ';',
                'closing': ';'
            },
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
    def expression_opening(self) -> str:
        return self.get_value('expression')['opening']

    @property
    def expression_closing(self) -> str:
        return self.get_value('expression')['closing']

    @property
    def expression(self) -> str:
        pattern = self.get_value('expression')['pattern']
        opening = self.get_value('expression')['opening']
        closing = self.get_value('expression')['closing']
        
        return f'^{opening}{pattern}{closing}$'

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
 