# pylint: disable=C0114,C0115,C0116
from typing import Any
import logging
import discord
from discord.ext import commands

from .emojimanager import EmojiManager
from .emojipareser import EmojiParser
from .exceptions import EmojiError
from .views import (
    EmojiEmbed,
    EmojiErrorEmbed,
    EmojiListPage
)

# Decorator for checking permission
def emoji_managable():
    def predicate(ctx: discord.ApplicationContext):
        return ctx.channel.permissions_for(ctx.author).manage_emojis
    return commands.check(predicate=predicate)

class EmojiCog(commands.Cog):
    emoji_commands = discord.SlashCommandGroup(
        name='emoji',
        description='Command group for managing custom emoji.',
        guild_only=True
    )

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('fukurou.emoji')

    @emoji_commands.command(
        name='add',
        description='Add a custom emoji to the server.'
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
    @emoji_managable()
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
            self.logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to upload **{name}**', error=e),
                ephemeral=True
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

    @emoji_commands.command(
        name="delete",
        description="Delete the emoji from the server."
    )
    @discord.commands.option(
        input_type=str,
        name='name',
        description='Name of the emoji to delete.',
        required=True
    )
    @emoji_managable()
    async def delete(self,
                     ctx: discord.ApplicationContext,
                     name: str):
        try:
            EmojiManager().delete(guild_id=ctx.guild.id, emoji_name=name)
        except EmojiError as e:
            self.logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to delete **{name}**', error=e),
                ephemeral=True
            )
        else:
            await ctx.respond(
                embed=EmojiEmbed(description=f'**{name}** has been deleted!')
            )

    @emoji_commands.command(
        name="rename",
        description="Rename the emoji."
    )
    @discord.commands.option(
        input_type=str,
        name='old_name',
        description='Name of the emoji you want to rename.',
        required=True
    )
    @discord.commands.option(
        input_type=str,
        name='new_name',
        description='New name for the emoji.',
        required=True
    )
    @emoji_managable()
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
                embed=EmojiErrorEmbed(description=e.message_backticked()),
                ephemeral=True
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
        name="replace",
        description="Replace the image of the emoji."
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
    @emoji_managable()
    async def replace(self,
                      ctx: discord.ApplicationContext,
                      name: str,
                      file: discord.Attachment):
        # This task can take longer than 3 seconds
        await ctx.defer()

        try:
            EmojiManager().replace(
                guild_id=ctx.guild.id,
                uploader=ctx.author.id,
                emoji_name=name,
                attachment=file
            )
        except EmojiError as e:
            self.logger.error(e.message_double_quoted())
            await ctx.respond(
                embed=EmojiErrorEmbed(description=f'Failed to upload **{name}**', error=e),
                ephemeral=True
            )
        else:
            await ctx.followup.send(
                file=await file.to_file(),
                embed=EmojiEmbed(
                    description=f'**{name}** is replaced!',
                    image_url=f'attachment://{file.filename}',
                    author=ctx.author
                )
            )

    @emoji_commands.command(
        name='list',
        description='Show a list of emoji in the server.'
    )
    @discord.commands.option(
        input_type=str,
        name='keyword',
        discription='Keyword to search for.',
        required=False
    )
    async def list(self, ctx: discord.ApplicationContext, keyword: str):
        emoji_list = EmojiManager().list(
            user_id=ctx.author.id,
            guild_id=ctx.guild.id,
            keyword=keyword
        )

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

            # Must have MANAGE_WEBHOOKS permission!
            webhook = await message.channel.create_webhook(name=message.author.name)
            await webhook.send(
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                file=discord.File(
                    fp=EmojiManager().get_file_loc(guild_id=message.guild.id, emoji=emoji),
                    filename=emoji.file_name
                )
            )

            await webhook.delete()
        except discord.Forbidden:
            # Send embedded Emoji when there's no permission to create webhook.
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
            self.logger.error('Cannot send emoji to the user(%d): %s', message.author.id, e.args)
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

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: Any):
        if isinstance(error, discord.CheckFailure):
            description = "You don't have a permission."
        else:
            description='Unknown error has occured.'

        await ctx.response.send_message(
            embed=EmojiErrorEmbed(description=description),
            ephemeral=True
        )
