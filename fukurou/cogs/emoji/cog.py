# pylint: disable=missing-function-docstring

import discord
from discord import Guild
from discord.ext import commands

from fukurou.logging import logger
from .emojimanager import EmojiManager, GuildEmojiManager
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
            # TODO: Insert emoji save method here.
            pass
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
            # TODO: Insert emoji delete method here
            pass
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
        # TODO: Insert emoji rename method here
        pass

        if result is True:
            # TODO: Insert emoji get method here
            emoji = 'Here'
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
        #TODO: Insert emoji list method here
        pass

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

        # TODO: Insert emoji get method here
        emoji = 'Here'
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
        # TODO: Insert emoji increase_usecount method here

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        EmojiManager().add_managers(guild_ids=self.bot.guilds)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        EmojiManager().add_manager(guild_id=guild.id)
