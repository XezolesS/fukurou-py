from __future__ import annotations
from abc import ABC
from typing import Any
from dataclasses import dataclass

from fukurou.patterns import classproperty

@dataclass
class BaseConfig(ABC):
    """
    Abstract class for the Config.

    A Config must be a top-level object in the JSON file.

    To implement a Config, you should:
    - Decorate a class with `dataclasses.dataclass`
    - Specify a value of `file_name` property.
    - Implement `from_dict` method to structurize and validate JSON data. 
    - Add fields and their default values.

    :cvar file_name: Name of the config file.
    """
    #pylint: disable=no-self-argument
    @classproperty
    def file_name(cls) -> str:
        """
        Name of the config file.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> BaseConfig:
        raise NotImplementedError

@dataclass
class BaseSubConfig(ABC):
    """
    Abstract class for a SubConfig.

    A SubConfig represents a non-top-level object in a JSON file.

    To implement a SubConfig, you should:
    - Decorate a class with `dataclasses.dataclass`
    - Implement `from_dict` method to structurize and validate JSON data. 
    - Add fields and their default values.
    """
    @classmethod
    def from_dict(cls, json_obj: dict[Any]) -> BaseSubConfig:
        raise NotImplementedError
