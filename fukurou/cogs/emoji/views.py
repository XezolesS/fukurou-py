from datetime import datetime
import discord
from discord import (
    Guild,
    User,
    Member,
    Embed,
    EmbedField,
    ButtonStyle,
    ApplicationCommandInvokeError
)
from discord.colour import Colour
from discord.ext.pages import Paginator, PaginatorButton

from .data import Emoji, EmojiList
from .exceptions import (
    EmojiError,
    EmojiCapacityExceededError,
    EmojiDatabaseError,
    EmojiExistsError,
    EmojiFileDownloadError,
    EmojiFileExistsError,
    EmojiFileIOError,
    EmojiFileTooLargeError,
    EmojiFileTypeError,
    EmojiInvalidNameError,
    EmojiNotFoundError,
    EmojiNotReadyError,
)

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
                 error: ApplicationCommandInvokeError | None = None):
        super().__init__(
            colour=Colour.red(),
            title=title,
            description=description
        )

        if error is not None:
            self.__set_content(error=error)

    def __set_content(self, error: ApplicationCommandInvokeError):
        # TODO:
        # `desc` is not signed in certain circumstances.
        # and may need cleaner code?
        desc = error.original
        match error:
            case discord.CheckFailure():
                desc = "Sorry, but you don't have permission to run this command!"
            case discord.ApplicationCommandInvokeError():
                e_args = error.original.args
                match error.original:
                    case EmojiCapacityExceededError():
                        desc = (
                            "You can't upload more Emoji on this server!\n"
                            f'The maximum capacity is `{e_args[0]}`.'
                        )
                    case EmojiDatabaseError():
                        desc = (
                            'Database operation failed!\n'
                            'Please contact the owner of the bot.'
                        )
                    case EmojiExistsError():
                        desc = (
                            f'Emoji `{e_args[0]}` already exists!'
                        )
                    case EmojiFileDownloadError():
                        desc = (
                            'Sorry, but I could not download your file...'
                        )
                    case EmojiFileExistsError():
                        desc = (
                            f'The uploaded Emoji file is already assigned to `{e_args[0]}`!\n'
                        )
                    case EmojiFileIOError():
                        desc_map = {
                            'r': 'Sorry, but I could not read the file...',
                            'w': 'Sorry, but I could not save the file...'
                        }

                        try:
                            desc = desc_map[e_args[0]]
                        except KeyError:
                            desc = 'no'

                    case EmojiFileTooLargeError():
                        desc = (
                            f'Your Emoji is too big! (`{e_args[0]}KB`)\n'
                            f'The size limit is `{e_args[1]}KB`.'
                        )
                    case EmojiFileTypeError():
                        desc = (
                            f'`.{e_args[0]}` is not supported!'
                        )
                    case EmojiInvalidNameError():
                        desc = (
                            f'`{e_args[0]}` is invalid name!\n'
                            f'Format: ||{e_args[1]}||'
                        )
                    case EmojiNotFoundError():
                        desc = (
                            f'There is no Emoji named `{e_args[0]}`!'
                        )
                    case EmojiNotReadyError():
                        desc = (
                            'Emoji service is not ready!\n'
                            'Please contact the owner of the bot.'
                        )
                    case EmojiError():
                        desc = (
                            'Unknown Emoji error has occured!\n'
                            'Please contact the owner of the bot.'
                        )
                    case _:
                        pass
            case _:
                desc = 'Unknown error has occured!'

        self.add_field(name='Something went wrong!', value=desc)

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
            title += f" Searched for '{self.keyword}'"

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
