from .configs import BaseConfig, add_config

class FukurouConfig(BaseConfig):
    @property
    def name(self) -> str:
        return 'fukurou'

    @property
    def keys(self) -> list[str]:
        return [
            'client_id',
            'permission',
            'token'
        ]

    @property
    def client_id(self) -> str:
        return self.get_value('client_id')

    @property
    def permission(self) -> str:
        return self.get_value('permission')

    @property
    def token(self) -> str:
        return self.get_value('token')

add_config(FukurouConfig())
