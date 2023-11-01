from datetime import datetime
from discord import (
    Guild,
    User,
    Member,
    Embed,
    EmbedField,
    ButtonStyle
)
from discord.colour import Colour
from discord.ext.pages import Paginator, PaginatorButton

from .data import Emoji, EmojiList
from .exceptions import EmojiError

class EmojiEmbed(Embed):
    def __init__(self,
                 title: str | None = None,
                 description: str | None = None,
                 image_url: str | None = None,
                 author: Member | User | None = None):
        super().__init__(
            colour=Colour.nitro_pink(),
            title=title,
            description=description
        )

        if image_url is not None:
            self.set_image(url=image_url)

        if author is not None:
            self.set_author(
                name=author.display_name,
                url=author.jump_url,
                icon_url=author.display_avatar
            )

class EmojiErrorEmbed(Embed):
    def __init__(self,
                 title: str | None = None,
                 description: str | None = None,
                 error: EmojiError | None = None):
        super().__init__(
            colour=Colour.red(),
            title=title,
            description=description
        )

        if error is not None:
            self.add_field(name=error.desc, value=error.message_backticked())

class EmojiListPage(Paginator):
    def __init__(self, guild: Guild, emoji_list: list[Emoji], keyword: str = None, **kwargs):
        self.guild = guild
        self.keyword = keyword

        super().__init__(pages=self.__build_pages(emoji_list=emoji_list), **kwargs)

        self.custom_buttons = [
            PaginatorButton('first', label='⯬', style=ButtonStyle.green),
            PaginatorButton('prev', label='🠜', style=ButtonStyle.green),
            PaginatorButton('page_indicator', style=ButtonStyle.gray, disabled=True),
            PaginatorButton('next', label='🠞', style=ButtonStyle.green),
            PaginatorButton('last', label='⯮', style=ButtonStyle.green)
        ]

    def __build_pages(self, emoji_list: EmojiList):
        emoji_count = len(emoji_list)
        title = 'Emoji List'

        if self.keyword is not None:
            title += f' Searched for "{self.keyword}"'

        emoji_pages = []
        for index, emoji in enumerate(emoji_list):
            # Create new embed page
            if index % 10 == 0:
                embed = Embed(title=f'{title}')
                embed.set_footer(text=f'Total {emoji_count} of emojis are searched!')
                emoji_pages.append(embed)

            uploader = self.guild.get_member(emoji.uploader_id)
            uploader = uploader.mention if uploader is not None else '*<Unknown>*'

            local_tz = datetime.now().tzinfo
            created_at = emoji.created_at.astimezone(tz=local_tz).strftime('%Y/%m/%d %H:%M:%S')

            use_count_str = f'({emoji.user_use_count}/{emoji.guild_use_count})'

            # Add emoji info
            embed.add_field(
                name=f':small_blue_diamond: {use_count_str} {emoji.emoji_name}',
                value=f'Uploaded by {uploader} at `{created_at}`',
                inline=False
            )

        return emoji_pages
