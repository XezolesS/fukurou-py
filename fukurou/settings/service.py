import os
import logging
import dataclasses
import msgpack

from pathlib import Path
from typing import Type, NewType

from fukurou.patterns import SingletonMeta
from fukurou.settings.interfaces import BaseSetting

SETTINGS_DIR = Path('settings/')

Setting = NewType('Setting', BaseSetting)

class CogSettingService:
    def __init__(self, setting: Type[Setting]):
        self.__setting = setting
        self.__dir = SETTINGS_DIR / setting.getdir()
        self.__data: dict[int, Setting] = {}

    def __getitem__(self, key) -> Setting:
        return self.__data[key]

    def _get_file(self, guild_id: int) -> Path:
        return self.__dir / f'{guild_id}.fkst'

    def _dump(self, guild_id: int) -> None:
        setting_data = self.__data[guild_id]

        if not isinstance(setting_data, BaseSetting):
            raise TypeError(f'must be Base Setting, not {type(setting_data)}', setting_data)

        file_path = self._get_file(guild_id)
        data = dataclasses.asdict(setting_data)

        with open(file_path, 'wb') as file:
            msgpack.dump(data, file)

    def _load(self, guild_id: int) -> Setting:
        file_path = self._get_file(guild_id)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        with open(file_path, 'rb') as file:
            data = msgpack.load(file)

        return self.__setting(**data)

    def load(self, *guild_ids: int) -> None:
        self.__dir.mkdir(exist_ok=True)

        for guild_id in guild_ids:
            try:
                self.__data[guild_id] = self._load(guild_id)
            except FileNotFoundError:
                # Create a new file if it does not exist.
                self.__data[guild_id] = self.__setting()
                self._dump(guild_id)

    def reload(self) -> None:
        self.load(*self.__data.keys())

class SettingService(metaclass=SingletonMeta):
    def __init__(self):
        self.logger = logging.getLogger('fukurou.settings')
        self.settings: dict[Type[Setting], CogSettingService] = {}

    def __getitem__(self, key) -> Setting:
        return self.get(key)

    def add(self, setting: Type[Setting]) -> None:
        if setting in self.settings:
            self.logger.warning('%s is already added.', setting.__name__)
            return

        os.makedirs(os.path.join(SETTINGS_DIR, setting.getdir()), exist_ok=True)

        self.settings[setting] = CogSettingService(setting=setting)

    def get(self, setting: Type[Setting]) -> CogSettingService | None:
        try:
            return self.settings[setting]
        except KeyError:
            return None
