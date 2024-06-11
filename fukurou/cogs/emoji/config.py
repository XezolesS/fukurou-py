from __future__ import annotations
import os
from typing import Any
from dataclasses import dataclass, field

from fukurou.configs import BaseConfig, BaseSubConfig

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
class EmojiConstraintConfig(BaseSubConfig):
    capacity: int = -1
    maxsize: int = 8192

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiConstraintConfig:
        return EmojiConstraintConfig(
            capacity=json_obj['capacity'],
            maxsize=json_obj['maxsize']
        )

@dataclass
class EmojiGlobalConstraintConfig(BaseSubConfig):
    capacity: int = 500
    maxsize: int = 1024
    overrides: dict[int, EmojiConstraintConfig] = field(
        default_factory=lambda: {"GUILD_ID": EmojiConstraintConfig()}
    )

    def __post_init__(self):
        self.default_constraint = EmojiConstraintConfig(
            capacity=self.capacity,
            maxsize=self.maxsize
        )

    def __getitem__(self, key: int) -> EmojiGlobalConstraintConfig:
        try:
            return self.overrides[key]
        except KeyError:
            return self.default_constraint

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiGlobalConstraintConfig:
        constraints = {}
        for guild_id, constraint in json_obj['overrides'].items():
            try:
                constraints[int(guild_id)] = constraint
            except ValueError:
                pass    # Ignore ValueError

        return EmojiGlobalConstraintConfig(
            capacity=json_obj['capacity'],
            maxsize=json_obj['maxsize'],
            overrides=constraints
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
    expression: EmojiExpressionConfig = field(default_factory=EmojiExpressionConfig)
    constraints: EmojiGlobalConstraintConfig = field(default_factory=EmojiGlobalConstraintConfig)
    database: EmojiDatabaseConfig = field(default_factory=EmojiDatabaseConfig)
    storage: EmojiStorageConfig = field(default_factory=EmojiStorageConfig)

    @classmethod
    def get_file_name(cls) -> str:
        return 'emoji.json'

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> EmojiConfig:
        return EmojiConfig(
            expression=EmojiExpressionConfig.from_dict(json_obj['expression']),
            constraints=EmojiGlobalConstraintConfig.from_dict(json_obj['constraints']),
            database=EmojiDatabaseConfig.from_dict(json_obj['database']),
            storage=EmojiStorageConfig.from_dict(json_obj['storage'])
        )
