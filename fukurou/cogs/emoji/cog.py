from datetime import datetime
import discord
from discord import Guild
from discord.ext import commands, pages

from fukurou.logging import logger
from .data import Emoji
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
            embed = discord.Embed(
                color=discord.Color.red(),
                description = f'Failed to upload **{name}**'
            )
            embed.add_field(
                name=e.desc,
                value=e.message_backticked()
            )

            await ctx.respond(embed=embed)

            logger.error(e.message_double_quoted())
            return

        embed = discord.Embed(
            color = discord.Color.green(),
            description = f'**{name}** is uploaded!'
        )
        embed.set_author(
            name=ctx.author.display_name,
            url=ctx.author.jump_url,
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_image(url=f'attachment://{file.filename}')

        uploaded = await file.to_file()

        await ctx.followup.send(file=uploaded, embed=embed)

    @emoji_commands.command()
    async def delete(self,
                     ctx: discord.ApplicationContext,
                     name: str):
        try:
            self.image_handlers[ctx.guild.id].delete_emoji(name=name)
        except EmojiError as e:
            embed = discord.Embed(
                color=discord.Color.red(),
                description = f'Failed to delete **{name}**'
            )
            embed.add_field(
                name=e.desc,
                value=e.message_backticked()
            )

            await ctx.respond(embed=embed)

            logger.error(e.message_double_quoted())
            return

        embed = discord.Embed(
            color = discord.Color.green(),
            description = f'**{name}** has been deleted!'
        )
        embed.set_author(
            name=ctx.author.display_name,
            url=ctx.author.jump_url,
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.respond(embed=embed)

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
            file = discord.File(fp=emoji.file_path, filename=emoji.file_name)

            embed.set_image(url=f'attachment://{file.filename}')
        else:
            embed.color = discord.Color.red()
            embed.description = f'Cannot rename emoji `{old_name}` to `{new_name}`!'

        await ctx.respond(file=file, embed=embed)

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
            embed = discord.Embed(
                color=discord.Color.red(),
                description = f"I can't find the emoji that contains `{keyword}` in its name!"
            )

            await ctx.respond(embed=embed)

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

        author = message.author
        guild_id = message.guild.id

        emoji = self.image_handlers[guild_id].get_emoji(image_name)
        if emoji is None:
            return

        try:
            await message.delete()

            file = discord.File(fp=emoji.file_path, filename=emoji.file_name)

            embed = discord.Embed(colour=discord.Color.green())
            embed.set_author(
                name=author.display_name,
                url=author.jump_url,
                icon_url=author.display_avatar.url
            )
            embed.set_image(url=f'attachment://{emoji.file_name}')

            await message.channel.send(file=file, embed=embed)
        except discord.DiscordException as e:
            logger.error('Cannot send emoji to the user(%d): %s', author.id, e.args)

        # Increase usecount when sending emoji succeed
        self.image_handlers[guild_id].increase_emoji_usecount(
            user=author.id,
            name=emoji.emoji_name
        )

    @commands.Cog.listener('on_ready')
    async def load_guild_emoji(self):
        for guild in self.bot.guilds:
            self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

    @commands.Cog.listener('on_guild_join')
    async def init_guild_emoji(self, guild: discord.Guild):
        self.image_handlers[guild.id] = ImageHandler(guild_id=guild.id)

class EmojiListPage(pages.Paginator):
    def __init__(self, guild: Guild, emoji_list: list[Emoji], keyword: str = None, **kwargs):
        self.guild = guild
        self.keyword = keyword
        super().__init__(pages=self.__build_pages(emoji_list=emoji_list), **kwargs)

        self.custom_buttons = [
            pages.PaginatorButton(
                'first',
                label = '⯬',
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                'prev',
                label = '🠜',
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                'page_indicator',
                style = discord.ButtonStyle.gray,
                disabled = True
            ),
            pages.PaginatorButton(
                'next',
                label='🠞',
                style = discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                'last',
                label='⯮',
                style=discord.ButtonStyle.green
            ),
        ]

    def __build_pages(self, emoji_list: list[Emoji]):
        emoji_count = len(emoji_list)
        title = 'Emoji List'

        if self.keyword is not None:
            title += f' Searched for "{self.keyword}"'

        emoji_pages = []
        for index, emoji in enumerate(emoji_list):
            # Create new embed page
            if index % 10 == 0:
                embed = discord.Embed(title=f'{title}')
                embed.set_footer(text=f'Total {emoji_count} of emojis are searched!')
                emoji_pages.append(embed)

            uploader = self.guild.get_member(emoji.uploader_id)
            uploader = uploader.mention if uploader is not None else '*<Unknown>*'

            local_tz = datetime.now().tzinfo
            created_at = emoji.created_at.astimezone(tz=local_tz).strftime('%Y/%m/%d %H:%M:%S')

            # Add emoji info
            embed.add_field(
                name = f':small_blue_diamond: {emoji.emoji_name}',
                value = f'Uploaded by {uploader} at `{created_at}`',
                inline = False
            )

        return emoji_pages
