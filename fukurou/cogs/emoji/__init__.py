from .config import EmojiConfig
from .cog import EmojiCog

def setup(bot):
    EmojiConfig().load()
    bot.add_cog(EmojiCog(bot))
