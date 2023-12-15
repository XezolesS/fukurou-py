import re

from .config import EmojiConfig

class EmojiParser:
    @classmethod
    def match(cls, text: str) -> bool:
        return re.match(EmojiConfig().expression.pattern, text) is not None

    @classmethod
    def parse(cls, text: str) -> str | None:
        if not EmojiParser.match(text=text):
            return None

        opening = EmojiConfig().expression.opening
        closing = EmojiConfig().expression.closing

        parsed = text
        parsed = re.sub(f'^{opening}', '', parsed, 1)
        parsed = re.sub(f'{closing}$', '', parsed, 1)

        return parsed
