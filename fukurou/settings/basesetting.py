from os
from abc import ABC, abstractmethod
from typing import Any

class BaseSetting(ABC):
    @property
    @abstractmethod
    def file_name(self) -> str:
        """
        Name of the setting file.
        """
        raise NotImplementedError
    
    