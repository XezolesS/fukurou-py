from fukurou.configs import BaseConfig, add_config

class ExchangeConfig(BaseConfig):
    @property
    def name(self) -> str:
        return 'exchange'

    @property
    def keys(self) -> list[str]:
        return [
            'token_koreaexim',
        ]

    @property
    def default_values(self) -> dict[str, any]:
        return {
            'token_koreaexim': 'TOKEN HERE'
        }

    @property
    def token_koreaexim(self) -> str:
        return self.get_value('token_koreaexim')

add_config(ExchangeConfig())
