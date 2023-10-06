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
            'database': 'sqlite',
            'storage': {
                'type': 'local',
                'directory': './image'
            }
        }

    @property
    def database(self) -> str:
        return self.get_value('database')

    @property
    def storage_type(self) -> str:
        return self.get_value('storage')['type']

    @property
    def storage_dir(self) -> str:
        return self.get_value('storage')['directory']

add_config(EmojiConfig())
