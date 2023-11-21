from typing import Any

class Singleton(type):
    __instances = {}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self not in self.__instances:
            self.__instances[self] = super(Singleton, self).__call__(*args, **kwds)
        return self.__instances[self]
