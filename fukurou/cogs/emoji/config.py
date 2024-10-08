from __future__ import annotations
import os
from typing import Any
from dataclasses import dataclass, field

from fukurou.configs import Config

@dataclass
class EmojiExpressionConfig(Config):
    name_pattern: str = '[a-zA-Z0-9_ -]+'
    opening: str = ';'
    closing: str = ';'
    ignore_spaces: bool = True

    def __post_init__(self) -> None:
        self.pattern = f'^{self.opening}{self.name_pattern}{self.closing}$'

@dataclass
class EmojiGuildConstraintsConfig(Config):
    capacity: int = -1
    maxsize: int = 8192

@dataclass
class EmojiConstraintsConfig(Config):
    capacity: int = 500
    maxsize: int = 1024
    overrides: dict[int, EmojiGuildConstraintsConfig] = field(
        default_factory=lambda: {"GUILD_ID": EmojiGuildConstraintsConfig()}
    )

    def __post_init__(self):
        self.default = EmojiGuildConstraintsConfig(
            capacity=self.capacity,
            maxsize=self.maxsize
        )

    def __getitem__(self, key: int) -> EmojiConstraintsConfig:
        try:
            return self.overrides[key]
        except KeyError:
            return self.default

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiConstraintsConfig:
        constraints = {}
        for guild_id, constraint in json_obj['overrides'].items():
            try:
                constraints[int(guild_id)] = constraint
            except ValueError:
                # TODO: warning log?
                pass    # Ignore ValueError

        return EmojiConstraintsConfig(
            capacity=json_obj['capacity'],
            maxsize=json_obj['maxsize'],
            overrides=constraints
        )

@dataclass
class EmojiDatabaseConfig(Config):
    type: str = 'sqlite'
    file: str = 'emoji.db'
    directory: str = './databases'

    def __post_init__(self):
        self.path = os.path.abspath(os.path.join(self.directory, self.file))

@dataclass
class EmojiStorageConfig(Config):
    type: str = 'local'
    directory: str = './images'

@dataclass
class EmojiConfig(Config, filename='emoji.json'):
    expression: EmojiExpressionConfig = field(default_factory=EmojiExpressionConfig)
    constraints: EmojiConstraintsConfig = field(default_factory=EmojiConstraintsConfig)
    database: EmojiDatabaseConfig = field(default_factory=EmojiDatabaseConfig)
    storage: EmojiStorageConfig = field(default_factory=EmojiStorageConfig)
