# pylint: disable=missing-function-docstring

import discord
from discord import Guild
from discord.ext import commands

from fukurou.logging import logger
from .emojipareser import EmojiParser
from .exceptions import EmojiError
from .image import (
    ImageHandlers,
    ImageHandler
)
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
        self.image_handlers = ImageHandlers()

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
            self.image_handlers[ctx.guild.id].save_emoji(name=name,
                                                         uploader=ctx.author.id,
                                                         attachment=file)
        except EmojiError as e:
            logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to upload **{name}**', error=e)
            )

            return

        embed = EmojiEmbed(
            description=f'**{name}** is uploaded!',
            image_url=f'attachment://{file.filename}',
            author=ctx.author
        )
        emoji_file = await file.to_file()

        await ctx.followup.send(file=emoji_file, embed=embed)

    @emoji_commands.command()
    async def delete(self,
                     ctx: discord.ApplicationContext,
                     name: str):
        try:
            self.image_handlers[ctx.guild.id].delete_emoji(name=name)
        except EmojiError as e:
            logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to delete **{name}**', error=e)
            )

            return

        embed = EmojiEmbed(
            description=f'**{name}** has been deleted!'
        )

        await ctx.respond(embed=embed)

    @emoji_commands.command()
    async def rename(self,
                     ctx: discord.ApplicationContext,
                     old_name: str,
                     new_name: str):
        # TODO: Rename exception handling
        result = self.image_handlers[ctx.guild.id].rename_emoji(old_name=old_name,
                                                                new_name=new_name)
        if result is True:
            emoji = self.image_handlers[ctx.guild.id].get_emoji(new_name)
            emoji_file = discord.File(fp=emoji.file_path, filename=emoji.file_name)

            embed = EmojiEmbed(
                description=f'Emoji `{old_name}` is now `{new_name}`!',
                image_url=f'attachment://{emoji_file.filename}',
                author=ctx.author
            )

            await ctx.respond(file=emoji_file, embed=embed)
        else:
            await ctx.respond(
                embed=EmojiErrorEmbed(
                    description=f'Cannot rename emoji `{old_name}` to `{new_name}`!'
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
        emoji_list = self.image_handlers[ctx.guild.id].emoji_list(keyword=keyword)

        if not emoji_list:
            if keyword is None:
                message = 'There is no emoji on the server!'
            else:
                message = f"I can't find the emoji that contains `{keyword}` in its name!"

            await ctx.respond(embed=EmojiErrorEmbed(description=message))

            return

        emoji_page = EmojiListPage(guild=ctx.guild, emoji_list=emoji_list, keyword=keyword)

        await emoji_page.respond(ctx.interaction, ephemeral=True)

    @commands.Cog.listener('on_message')
    async def on_emoji(self, message: discord.Message):
        # Filter message from itself
        if message.author.id == self.bot.user.id:
            return

        image_name = EmojiParser.parse(text=message.content)
        if image_name is None:
            return

        emoji = self.image_handlers[message.guild.id].get_emoji(image_name)
        if emoji is None:
            return

        try:
            await message.delete()

            emoji_file = discord.File(fp=emoji.file_path, filename=emoji.file_name)

            embed = EmojiEmbed(
                image_url=f'attachment://{emoji.file_name}',
                author=message.author
            )

            await message.channel.send(file=emoji_file, embed=embed)
        except discord.DiscordException as e:
            logger.error('Cannot send emoji to the user(%d): %s', message.author.id, e.args)

        # Increase usecount when sending emoji succeed
        self.image_handlers[message.guild.id].increase_emoji_usecount(
            user=message.author.id,
            name=emoji.emoji_name
        )

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        for guild in self.bot.guilds:
            self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)
