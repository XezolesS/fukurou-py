from .config import EmojiConfig
from .cog import EmojiCog
from fukurou.configs import NewConfigInterrupt

def setup(bot):
    EmojiConfig().load()
    bot.add_cog(EmojiCog(bot))
