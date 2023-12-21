from .base import BaseEmojiStorage
from .local import LocalEmojiStorage

def get_emoji_storage(sttype: str) -> BaseEmojiStorage:
    """
    Get an image storage controller for the Emoji.

    :param sttype: Type of the storage in string.
    :type sttype: str

    :return: Image storage IO controller.
    :rtype: BaseEmojiStorage

    :raises ValueError: If the `sttype` is invalid storage.
    """
    match sttype:
        case 'local':
            return LocalEmojiStorage()

    raise ValueError('There is no such storage', sttype)
