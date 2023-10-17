import re
import discord
from discord.ext import commands

from fukurou.logging import logger
from .emojipareser import EmojiParser
from .exceptions import EmojiError
from .image import (
    ImageHandlers,
    ImageHandler
)

class EmojiCog(commands.Cog):
    emoji_commands = discord.SlashCommandGroup(
        name='emoji',
        description='Command group for managing custom emoji.'
    )

    def __init__(self, bot):
        self.bot = bot
        self.image_handlers = ImageHandlers()

    @emoji_commands.command()
    async def upload(self,
                     ctx: discord.ApplicationContext,
                     name: str,
                     file: discord.Attachment):
        embed = discord.Embed()
        uploaded = None

        try:
            self.image_handlers[ctx.guild.id].save_emoji(name=name,
                                                         uploader=ctx.author.id,
                                                         file_url=file.url,
                                                         file_type=file.content_type)
        except EmojiError as e:
            embed.color = discord.Color.red()
            embed.description = f'Failed to upload **{name}**'
            embed.add_field(
                name=e.name,
                value=e.message_backticked()
            )

            logger.error(e.message_double_quoted())
        else:
            embed.color = discord.Color.green()
            embed.description = f'**{name}** is uploaded!'
            embed.set_author(
                name=ctx.author.display_name,
                url=ctx.author.jump_url,
                icon_url=ctx.author.display_avatar.url
            )
            embed.set_image(url=f'attachment://{file.filename}')

            uploaded = await file.to_file()

        await ctx.respond(file=uploaded, embed=embed)

    @emoji_commands.command()
    async def rename(self,
                     ctx: discord.ApplicationContext,
                     old_name: str,
                     new_name: str):
        result = self.image_handlers[ctx.guild.id].rename_emoji(old_name=old_name,
                                                                new_name=new_name)

        embed = discord.Embed()
        file = None
        if result is True:
            embed.color = discord.Color.green()
            embed.description = f'Emoji `{old_name}` is now `{new_name}`!'

            emoji = self.image_handlers[ctx.guild.id].get_emoji(new_name)
            file = discord.File(fp=emoji.path, filename=emoji.file_name)

            embed.set_image(url=f'attachment://{file.filename}')
        else:
            embed.color = discord.Color.red()
            embed.description = f'Cannot rename emoji `{old_name}` to `{new_name}`!'

        await ctx.respond(file=file, embed=embed)

    @commands.Cog.listener('on_message')
    async def on_emoji(self, message: discord.Message):
        # Filter message from itself
        if message.author.id == self.bot.user.id:
            return

        image_name = EmojiParser.parse(text=message.content)
        if image_name is None:
            return

        author = message.author
        guild_id = message.guild.id

        emoji = self.image_handlers[guild_id].get_emoji(image_name)
        if emoji is None:
            return

        file = discord.File(fp=emoji.path, filename=emoji.file_name)

        embed = discord.Embed(colour=discord.Color.green())
        embed.set_author(
            name=author.display_name,
            url=author.jump_url,
            icon_url=author.display_avatar.url
        )
        embed.set_image(url="attachment://" + emoji.file_name)

        await message.channel.send(file=file, embed=embed)
        await message.delete()

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        for guild in self.bot.guilds:
            self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)
