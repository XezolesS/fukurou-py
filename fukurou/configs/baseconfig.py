from abc import ABC, abstractmethod
import json
import os

class BaseConfig(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        return None

    @property
    def filename(self) -> str:
        if self.name is None:
            return None

        return self.name + ".json"

    @property
    @abstractmethod
    def keys(self) -> list[str]:
        return None

    @property
    def values(self) -> dict[str, any]:
        return self.__values

    def load(self, directory: str = None):
        config_path = os.path.join(directory, self.filename)

        # Make new config file if it doesn't exist.
        if not os.path.exists(config_path):
            self.init(directory = directory)

        with open(config_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.__values = json.loads(content)

    def init(self, directory: str = None):
        if not os.path.exists(directory):
            os.makedirs(directory)

        config_path = os.path.join(directory, self.filename)
        with open(config_path, "w", encoding="utf-8") as file:
            values: dict[str, str] = dict()
            for key in self.keys:
                values[key] = f"{key}_value"

            json.dump(values, file, indent=4)

    def get_value(self, key: str = None) -> any:
        if key is None:
            return None

        return self.values[key]
