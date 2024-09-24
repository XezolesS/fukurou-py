import re

from fukurou.cogs.emoji.config import EmojiConfig

class EmojiParser:
    def __init__(self, config: EmojiConfig):
        self.pattern = config.expression.pattern
        self.opening = config.expression.opening
        self.closing = config.expression.closing

    def match(self, text: str) -> bool:
        return re.match(self.pattern, text) is not None

    def parse(self, text: str) -> str | None:
        if not self.match(text=text):
            return None

        parsed = text
        parsed = re.sub(f'^{self.opening}', '', parsed, 1)
        parsed = re.sub(f'{self.closing}$', '', parsed, 1)

        return parsed
