import discord
from discord.ext import commands

from .config import ExchangeConfig
from .koreaexim import (
    KoreaExIm,
    CURRENCIES
)

class ExchangeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__init_koreaexim()

    def __init_koreaexim(self):
        token = ExchangeConfig().token_koreaexim
        self.wrapper = KoreaExIm(token)

    @discord.slash_command()
    async def exchange(self, ctx: discord.ApplicationContext,
                       source: discord.Option(str, choices=CURRENCIES),
                       target: discord.Option(str, choices=CURRENCIES),
                       value: float):
        self.wrapper.load()

        src_name = self.wrapper.name(source)
        trg_name = self.wrapper.name(target)
        src_base_rate = self.wrapper.base_rate(source)
        trg_base_rate = self.wrapper.base_rate(target)
        exchanged = self.wrapper.exchange(source_currency=source,
                                          target_currency=target,
                                          amount=value)
        base_exchanged = src_base_rate / trg_base_rate

        response = discord.Embed(colour=discord.Color.green(), title=f"{source} → {target}")
        response.add_field(name=f"{src_name}", value=f"{value:g} {source}")
        response.add_field(name=f"{trg_name}", value=f"{exchanged:g} {target}")
        response.set_footer(text=f"Base Rate: 1 {source} → {base_exchanged:g} {target}\n"
                            + "from Export-Import Bank of Korea")

        await ctx.respond(embed=response)
