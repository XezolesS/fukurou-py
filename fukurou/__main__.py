from . import fukuroubot as fbot
from . import configs

if __name__ == '__main__':
    fbot.run(token=configs.get_config('fukurou').token)
