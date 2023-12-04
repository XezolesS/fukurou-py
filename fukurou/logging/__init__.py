from .init import init_logger
from fukurou.patterns import SingletonMeta

class TempLogger(metaclass=SingletonMeta):
    def __init__(self):
        self.logger = None

    def init(self):
        self.logger = init_logger()
