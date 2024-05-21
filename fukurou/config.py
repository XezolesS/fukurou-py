from typing import Any

from .configs.baseconfig import BaseConfig

class BotConfig(BaseConfig):
    @property
    def file_name(self) -> str:
        return 'fukurou.json'

    def __init__(self):
        self.token: str = None
        self.extensions: list[str] = None
        self.logging: self.LoggingConfig = None

        super().__init__(defcon_dir=__file__)

    def map(self, json_obj: dict[Any]) -> None:
        # Credentials
        self.token = json_obj['token']

        # Cogs to load
        self.extensions = json_obj['extensions']

        # Logging
        self.logging = json_obj['logging']

    class LoggingConfig:
        def __init__(self, json_obj: dict[Any]):
            self.directory = json_obj['directory']
            self.max_log_files = json_obj['max_log_files']
            self.format = self.LoggingFormatConfig(json_obj['format'])

        class LoggingFormatConfig:
            def __init__(self, json_obj: dict[Any]):
                self.file_name = json_obj['file_name']
                self.file_date = json_obj['file_date']
                self.log_msg = json_obj['log_msg']
                self.log_date = json_obj['log_date']
