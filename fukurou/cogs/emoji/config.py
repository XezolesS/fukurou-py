from __future__ import annotations
import os
from typing import Any
from dataclasses import dataclass, field

from fukurou.configs import BaseConfig, BaseSubConfig
from fukurou.patterns import classproperty

@dataclass
class EmojiExpressionConfig(BaseSubConfig):
    name_pattern: str = '[a-zA-Z0-9_ -]+'
    opening: str = ';'
    closing: str = ';'
    ignore_spaces: bool = True

    def __post_init__(self) -> None:
        self.pattern = f'^{self.opening}{self.name_pattern}{self.closing}$'

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiExpressionConfig:
        return EmojiExpressionConfig(
            name_pattern=json_obj['name_pattern'],
            opening=json_obj['opening'],
            closing=json_obj['closing'],
            ignore_spaces=json_obj['ignore_spaces']
        )

@dataclass
class EmojiGuildConstraintConfig(BaseSubConfig):
    guild_id: int = -1
    capacity: int = 500
    maxsize: int = 1024

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiGuildConstraintConfig:
        return EmojiGuildConstraintConfig(
            guild_id=json_obj['guild_id'],
            capacity=json_obj['capacity'],
            maxsize=json_obj['maxsize']
        )

@dataclass
class EmojiConstraintsConfig(BaseSubConfig):
    capacity: int = 500
    maxsize: int = 1024
    overrides: list[EmojiGuildConstraintConfig] = field(
        default_factory=lambda: [EmojiGuildConstraintConfig()]
    )

    def __post_init__(self):
        self.default_constraint = EmojiGuildConstraintConfig(
            guild_id=-1,
            capacity=self.capacity,
            maxsize=self.maxsize
        )

    def __getitem__(self, key: int) -> EmojiGuildConstraintConfig:
        try:
            return self.overrides[key]
        except KeyError:
            return self.default_constraint

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiConstraintsConfig:
        return EmojiConstraintsConfig(
            capacity=json_obj['capacity'],
            maxsize=json_obj['maxsize'],
            overrides=[
                EmojiGuildConstraintConfig.from_dict(ovrd_obj) for ovrd_obj in json_obj['overrides']
            ]
        )

@dataclass
class EmojiDatabaseConfig(BaseSubConfig):
    type: str = 'sqlite'
    file: str = 'emoji.db'
    directory: str = './databases'

    def __post_init__(self):
        self.path = os.path.abspath(os.path.join(self.directory, self.file))

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiDatabaseConfig:
        return EmojiDatabaseConfig(
            type=json_obj['type'],
            file=json_obj['file'],
            directory=json_obj['directory']
        )

@dataclass
class EmojiStorageConfig(BaseSubConfig):
    type: str = 'local'
    directory: str = './images'

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiStorageConfig:
        return EmojiStorageConfig(
            type=json_obj['type'],
            directory=json_obj['directory']
        )


@dataclass
class EmojiConfig(BaseConfig):
    #pylint: disable=no-self-argument
    expression: EmojiExpressionConfig = field(default_factory=EmojiExpressionConfig)
    constraints: EmojiConstraintsConfig = field(default_factory=EmojiConstraintsConfig)
    database: EmojiDatabaseConfig = field(default_factory=EmojiDatabaseConfig)
    storage: EmojiStorageConfig = field(default_factory=EmojiStorageConfig)

    @classproperty
    def file_name(cls) -> str:
        return 'emoji.json'

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiConfig:
        return EmojiConfig(
            expression=EmojiExpressionConfig.from_dict(json_obj['expression']),
            constraints=EmojiConstraintsConfig.from_dict(json_obj['constraints']),
            database=EmojiDatabaseConfig.from_dict(json_obj['database']),
            storage=EmojiStorageConfig.from_dict(json_obj['storage'])
        )
