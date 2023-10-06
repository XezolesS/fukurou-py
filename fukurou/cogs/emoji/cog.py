import re
import discord
from discord.ext import commands
from typing import TypedDict

from fukurou.logging import logger
from .image import ImageHandler

class EmojiCog(commands.Cog):

    emoji_commands = discord.SlashCommandGroup(
        name='emoji',
        description='Command group for managing custom emoji.'
    )

    def __init__(self, bot):
        self.bot = bot
        self.image_handlers = ImageHandlers()

    @emoji_commands.command()
    async def upload(self, ctx):
        await ctx.respond('Upload command')

    @emoji_commands.command()
    async def rename(self, ctx):
        await ctx.respond('Rename command')

    @commands.Cog.listener('on_message')
    async def on_emoji(self, message: discord.Message):
        # Filter message from itself
        if message.author.id == self.bot.user.id:
            return

        if not re.match('^;[a-zA-Z0-9_-]+;$', message.content):
            return

        author = message.author

        embed = discord.Embed(colour=discord.Color.green())
        embed.set_author(
            name=author.display_name,
            url=author.jump_url,
            icon_url=author.display_avatar.url
        )
        embed.add_field(
            name='',
            value=f"We're testing {message.content}"
        )

        await message.channel.send(embed=embed)
        await message.delete()

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        for guild in self.bot.guilds:
            self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

class ImageHandlers(TypedDict):
    guild_id: int
    handler: ImageHandler
