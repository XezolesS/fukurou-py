import os

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BaseSetting(ABC):
    """
    Abstract class for the Setting.
    """
    def __init__(self, guild_id: int) -> None:
        self.guild_id = guild_id

    @classmethod
    @abstractmethod
    def getdir(cls) -> str:
        raise NotImplementedError
