from . import config
from .cog import ExchangeCog

def setup(bot):
    bot.add_cog(ExchangeCog(bot))
