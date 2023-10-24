from datetime import datetime
from discord import (
    ButtonStyle,
    Embed,
    Guild
)
from discord.ext.pages import Paginator, PaginatorButton

from .data import Emoji

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

    def __build_pages(self, emoji_list: list[Emoji]):
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

            # Add emoji info
            embed.add_field(
                name = f':small_blue_diamond: {emoji.emoji_name}',
                value = f'Uploaded by {uploader} at `{created_at}`',
                inline = False
            )

        return emoji_pages
