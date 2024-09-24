from typing import TypeVar

from fukurou.cogs.emoji.config import EmojiConfig
from fukurou.cogs.emoji.storage.base import BaseEmojiStorage
from fukurou.cogs.emoji.storage.local import LocalEmojiStorage

EmojiStorage = TypeVar('EmojiStorage', bound=BaseEmojiStorage)

def get_emoji_storage(config: EmojiConfig) -> EmojiStorage:
    """
    Get an image storage controller for the Emoji.

    Parameters
    ----------
    config : EmojiConfig
        Config instance

    Returns
    -------
    EmojiStorage
        EmojiStorage instance built by the config

    Raises
    ------
    ValueError
        If storage type is invalid
    """
    match config.storage.type.lower():
        case 'local':
            return LocalEmojiStorage(config)

    # TODO: Error logging?
    raise ValueError('There is no such storage', config.storage.type)
