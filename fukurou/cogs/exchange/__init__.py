from .config import ExchangeConfig
from .cog import ExchangeCog

def setup(bot):
    ExchangeConfig().load()
    bot.add_cog(ExchangeCog(bot))
