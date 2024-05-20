from .config import EmojiConfig
from .cog import EmojiCog

def setup(bot):
    bot.add_config(EmojiConfig)
    bot.add_cog(EmojiCog(bot))
