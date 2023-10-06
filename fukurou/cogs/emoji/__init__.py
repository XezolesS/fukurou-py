from . import config
from .cog import EmojiCog

def setup(bot):
    bot.add_cog(EmojiCog(bot))
