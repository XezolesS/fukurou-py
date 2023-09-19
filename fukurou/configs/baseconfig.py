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

        return self.name + '.json'

    @property
    @abstractmethod
    def keys(self) -> list[str]:
        return None

    @property
    def values(self) -> dict[str, any]:
        return self.__values

    @property
    def default_values(self) -> dict[str, any]:
        return {}

    def load(self, directory: str = None):
        config_path = os.path.join(directory, self.filename)

        # Make new config file if it doesn't exist.
        if not os.path.exists(config_path):
            self.init(directory = directory)

        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()

        self.__values = json.loads(content)

    def init(self, directory: str = None):
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Validate default value, raise exceptions if it's not valid
        invalid_keys = []
        for key in self.keys:
            try:
                self.default_values[key]
            except KeyError:
                invalid_keys.append(key)

        if len(invalid_keys) > 0:
            invalid_key_string = "{'" + "', '".join(invalid_keys) + "'}"
            error_message = 'Cannot find default value of the configs! '
            error_message += f'(Invalids: {invalid_key_string})'

            raise KeyError(error_message)

        # Create default config file.
        config_path = os.path.join(directory, self.filename)
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(self.default_values, file, indent=4)

    def get_value(self, key: str = None) -> any:
        if key is None:
            return None

        return self.values[key]
