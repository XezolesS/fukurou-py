from typing import Tuple

class EmojiError(Exception):
    @property
    def desc(self) -> str:
        """
        Short description of the error.
        """
        return 'Emoji Error'

    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args)

        self.message = message
        self.message_args = message_args

    def message_double_quoted(self) -> str:
        """
        Retrieve the formatted message with arguments enclosed by double-qoutes.

        :return: Formatted message. 
        :rtype: str
        """
        return self.message.replace('%s', '"%s"') % (self.message_args)

    def message_backticked(self) -> str:
        """
        Retrieve the formatted message with arguments enclosed by backticks.

        :return: Formatted message. 
        :rtype: str
        """
        return self.message.replace('%s', '`%s`') % (self.message_args)

class EmojiDatabaseError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Database Operation Failed'

class EmojiNameExistsError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Name Already Exists'

class EmojiFileExistsError(EmojiError):
    @property
    def desc(self) -> str:
        return 'File Already Exists'

    def __init__(self,
                 *args: object,
                 message: str = None,
                 message_args: Tuple = None,
                 file_name: str = None,
                 directory: str = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.file_name = file_name
        self.directory = directory

class EmojiFileDownloadError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Failed to Download File'

class EmojiFileSaveError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Failed to Save File'

class EmojiFileTypeError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Invalid File Type'

class EmojiInvalidNameError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Invalid Name Format'

class EmojiNotFoundError(EmojiError):
    @property
    def desc(self) -> str:
        return 'Emoji Not Found'
