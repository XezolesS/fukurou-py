from fukurou.configs import BaseConfig, add_config

class LoggingConfig(BaseConfig):
    @property
    def name(self) -> str:
        return 'logging'

    @property
    def keys(self) -> list[str]:
        return [
            'directory',
            'max_logs',
            'file_name',
            'file_time',
            'log_format',
            'log_time'
        ]

    @property
    def default_values(self) -> dict[str, any]:
        return {
            'directory': 'logs',
            'max_logs': 10,
            'file_name': '%(datetime)s_fukurou',
            'file_time': '%Y-%m-%d_%H-%M-%S',
            'log_format': '[%(asctime)s | %(levelname)s] %(name)s\t%(message)s',
            'log_time': '%m-%d-%Y %H:%M:%S'
        }

    @property
    def directory(self) -> str:
        return self.get_value('directory')

    @property
    def max_logs(self) -> int:
        return self.get_value('max_logs')

    @property
    def file_name(self) -> str:
        return self.get_value('file_name')

    @property
    def file_time(self) -> str:
        return self.get_value('file_time')

    @property
    def log_format(self) -> str:
        return self.get_value('log_format')

    @property
    def log_time(self) -> str:
        return self.get_value('log_time')

add_config(LoggingConfig())
