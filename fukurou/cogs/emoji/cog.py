# pylint: disable=missing-function-docstring

import discord
from discord.ext import commands

from fukurou.logging import logger
from .emojimanager import EmojiManager
from .emojipareser import EmojiParser
from .exceptions import EmojiError
from .views import (
    EmojiEmbed,
    EmojiErrorEmbed,
    EmojiListPage
)

class EmojiCog(commands.Cog):
    emoji_commands = discord.SlashCommandGroup(
        name='emoji',
        description='Command group for managing custom emoji.'
    )

    def __init__(self, bot):
        self.bot = bot

    @emoji_commands.command(
        name='add',
        description='Add custom emoji to the server.'
    )
    @discord.commands.option(
        input_type=str,
        name='name',
        description='Name of the emoji.',
        required=True
    )
    @discord.commands.option(
        input_type=discord.Attachment,
        name='file',
        description='Image file of the emoji.',
        required=True
    )
    async def add(self,
                  ctx: discord.ApplicationContext,
                  name: str,
                  file: discord.Attachment):
        # This task can take longer than 3 seconds
        await ctx.defer()

        try:
            EmojiManager().add(
                guild_id=ctx.guild.id,
                uploader=ctx.author.id,
                emoji_name=name,
                attachment=file
            )
        except EmojiError as e:
            logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to upload **{name}**', error=e)
            )
        else:
            await ctx.followup.send(
                file=await file.to_file(),
                embed=EmojiEmbed(
                    description=f'**{name}** is uploaded!',
                    image_url=f'attachment://{file.filename}',
                    author=ctx.author
                )
            )

    @emoji_commands.command()
    async def delete(self,
                     ctx: discord.ApplicationContext,
                     name: str):
        try:
            EmojiManager().delete(guild_id=ctx.guild.id, emoji_name=name)
        except EmojiError as e:
            logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to delete **{name}**', error=e)
            )
        else:
            await ctx.respond(
                embed=EmojiEmbed(description=f'**{name}** has been deleted!')
            )

    @emoji_commands.command()
    async def rename(self,
                     ctx: discord.ApplicationContext,
                     old_name: str,
                     new_name: str):
        try:
            EmojiManager().rename(
                guild_id=ctx.guild.id,
                old_name=old_name,
                new_name=new_name
            )
        except EmojiError as e:
            await ctx.respond(
                embed=EmojiErrorEmbed(description=e.message_backticked())
            )
        else:
            emoji = EmojiManager().get(guild_id=ctx.guild.id, emoji_name=new_name)

            await ctx.respond(
                file=discord.File(
                    fp=EmojiManager().get_file_loc(guild_id=ctx.guild.id, emoji=emoji),
                    filename=emoji.file_name
                ),
                embed=EmojiEmbed(
                    description=f'Emoji `{old_name}` is now `{new_name}`!',
                    image_url=f'attachment://{emoji.file_name}',
                    author=ctx.author
                )
            )

    @emoji_commands.command(
        name='list',
        description='Shows a list of emoji in the server.'
    )
    @discord.commands.option(
        input_type=str,
        name='keyword',
        discription='Keyword to search for.',
        required=False
    )
    async def list(self, ctx: discord.ApplicationContext, keyword: str):
        emoji_list = EmojiManager().list(guild_id=ctx.guild.id, keyword=keyword)

        if not emoji_list:
            if keyword is None:
                message = 'There is no emoji on the server!'
            else:
                message = f"I can't find the emoji that contains `{keyword}` in its name!"

            await ctx.response.send_message(
                embed=EmojiErrorEmbed(description=message),
                ephemeral=True
            )

            return

        emoji_page = EmojiListPage(guild=ctx.guild, emoji_list=emoji_list, keyword=keyword)
        await emoji_page.respond(ctx.interaction, ephemeral=True)

    @commands.Cog.listener('on_message')
    async def on_emoji(self, message: discord.Message):
        # Filter message from itself
        if message.author.id == self.bot.user.id:
            return

        emoji_name = EmojiParser.parse(text=message.content)
        if emoji_name is None:
            return

        emoji = EmojiManager().get(guild_id=message.guild.id, emoji_name=emoji_name)
        if emoji is None:
            return

        try:
            await message.delete()
            await message.channel.send(
                file=discord.File(
                    fp=EmojiManager().get_file_loc(guild_id=message.guild.id, emoji=emoji),
                    filename=emoji.file_name
                ),
                embed=EmojiEmbed(
                    image_url=f'attachment://{emoji.file_name}',
                    author=message.author
                )
            )
        except discord.DiscordException as e:
            logger.error('Cannot send emoji to the user(%d): %s', message.author.id, e.args)
        else:
            # Increase usecount when sending emoji succeed
            EmojiManager().increase_usecount(
                guild_id=message.guild.id,
                user_id=message.author.id,
                emoji_name=emoji_name
            )

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        for guild in self.bot.guilds:
            EmojiManager().register(guild_id=guild.id)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        EmojiManager().register(guild_id=guild.id)
