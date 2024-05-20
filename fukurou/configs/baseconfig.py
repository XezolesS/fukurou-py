import os
from abc import ABC, abstractmethod
from typing import Any

class BaseConfig(ABC):
    """
    Abstract class for the config. 
    Property `file_name` and method `map()` must be implemented.

    The name of the default config must be a form of `defcon_{file_name}`.
    Default config must be located under `data/` in the same directory of the source code.

    :cvar file_name: Name of the config file.
    """
    @property
    @abstractmethod
    def file_name(self) -> str:
        """
        Name of the config file.
        """
        raise NotImplementedError

    def __init__(self, defcon_dir: str = __file__):
        self.defcon_path = os.path.join(
            os.path.dirname(defcon_dir),
            os.path.join('data', 'defcon_' + self.file_name)
        )

    @abstractmethod
    def map(self, json_obj: dict[Any]) -> None:
        raise NotImplementedError
