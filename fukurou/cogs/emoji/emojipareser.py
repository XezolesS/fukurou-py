import re

from fukurou.configs import configs
from fukurou.logging import logger

class EmojiParser:
    @classmethod
    def match(cls, text: str) -> bool:
        return re.match(configs.get_config('emoji').expression, text) is not None

    @classmethod
    def parse(cls, text: str) -> str | None:
        if not EmojiParser.match(text=text):
            return None

        opening = configs.get_config('emoji').expression_opening
        closing = configs.get_config('emoji').expression_closing

        parsed = text
        parsed = re.sub(opening, '', parsed)
        parsed = re.sub(closing, '', parsed)

        return parsed
