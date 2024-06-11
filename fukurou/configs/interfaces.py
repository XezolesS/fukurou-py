from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass

@dataclass
class BaseConfig(ABC):
    """
    Abstract class for the Config.

    A Config must be a top-level object in the JSON file.

    To implement a Config, you should:
    - Decorate a class with `dataclasses.dataclass`
    - Specify a return value of `get_file_name` method.
    - Implement `from_dict` method to structurize and validate JSON data. 
    - Add fields and their default values.
    """
    @classmethod
    @abstractmethod
    def get_file_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
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
    @abstractmethod
    def from_dict(cls, json_obj: dict[Any]) -> BaseSubConfig:
        raise NotImplementedError
