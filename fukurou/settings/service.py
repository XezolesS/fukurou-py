import os
import logging
import json
import shutil
from typing import Type, NewType

from fukurou.patterns import SingletonMeta

FUKUROU_SETTINGS_DIR = 'settings/'

Setting = NewType('Setting')