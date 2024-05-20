import re

from fukurou.configs import get_config
from .config import EmojiConfig

class EmojiParser:
    @classmethod
    def match(cls, text: str) -> bool:
        config: EmojiConfig = get_config(config=EmojiConfig)
        return re.match(config.expression.pattern, text) is not None

    @classmethod
    def parse(cls, text: str) -> str | None:
        if not EmojiParser.match(text=text):
            return None

        config: EmojiConfig = get_config(config=EmojiConfig)
        opening = config.expression.opening
        closing = config.expression.closing

        parsed = text
        parsed = re.sub(f'^{opening}', '', parsed, 1)
        parsed = re.sub(f'{closing}$', '', parsed, 1)

        return parsed
