from typing import Any

from fukurou.configs import BaseConfig

class ExchangeConfig(BaseConfig):
    @property
    def file_name(self) -> str:
        return 'exchange.json'

    def __init__(self):
        self.token_koreaexim = None

        super().__init__(defcon_dir=__file__)

    def map(self, json_obj: dict[Any]) -> None:
        self.token_koreaexim = json_obj['token_koreaexim']
