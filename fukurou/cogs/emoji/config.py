#pylint: disable=C0114,C0115
import os
from typing import Any

from fukurou.configs import BaseConfig

class EmojiConfig(BaseConfig):
    @property
    def file_name(self) -> str:
        return 'emoji.json'

    def __init__(self):
        self.expression = None
        self.constraints = None
        self.database = None
        self.storage = None

        super().__init__(defcon_dir=__file__)

    def map(self, json_obj: dict[Any]) -> None:
        self.expression = self.EmojiExpressionConfig(json_obj['expression'])
        self.constraints = self.EmojiConstraintsConfig(json_obj['constraints'])
        self.database = self.EmojiDatabaseConfig(json_obj['database'])
        self.storage = self.EmojiStorageConfig(json_obj['storage'])

    class EmojiExpressionConfig:
        def __init__(self, json_obj: dict[Any]):
            self.name_pattern = json_obj['name_pattern']
            self.opening = json_obj['opening']
            self.closing = json_obj['closing']
            self.ignore_spaces = json_obj['ignore_spaces']
            self.pattern = f'^{self.opening}{self.name_pattern}{self.closing}$'

    class EmojiConstraintsConfig:
        class EmojiConstraintConfig:
            def __init__(self, json_obj: dict[Any]):
                self.capacity = json_obj['capacity']
                self.maxsize = json_obj['maxsize']

        def __init__(self, json_obj: dict[Any]):
            self.__default_value = self.EmojiConstraintConfig(json_obj)
            self.__overrides: dict[int, self.EmojiConstraintConfig] = {}

            for o in json_obj['overrides']:
                self.__overrides[o['guild_id']] = self.EmojiConstraintConfig(o)

        def __getitem__(self, key: int) -> EmojiConstraintConfig:
            try:
                return self.__overrides[key]
            except KeyError:
                return self.__default_value[key]

    class EmojiDatabaseConfig:
        def __init__(self, json_obj: dict[Any]):
            self.type = json_obj['type']
            self.file = json_obj['file']
            self.directory = json_obj['directory']
            self.path = os.path.abspath(os.path.join(self.directory, self.file))

    class EmojiStorageConfig:
        def __init__(self, json_obj: dict[Any]):
            self.type = json_obj['type']
            self.directory = json_obj['directory']
