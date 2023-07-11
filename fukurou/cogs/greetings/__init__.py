from .cog import GreetingsCog

def setup(bot):
    bot.add_cog(GreetingsCog(bot))
