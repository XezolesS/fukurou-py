from typing import Tuple

class EmojiError(Exception):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args)

        self.name = "Emoji Error"
        self.message = message
        self.message_args = message_args

    def message_double_quoted(self) -> str:
        return self.message.replace('%s', '"%s"') % (self.message_args)

    def message_backticked(self) -> str:
        return self.message.replace('%s', '`%s`') % (self.message_args)

class EmojiDatabaseError(EmojiError):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "Database Error"

class EmojiNameExistsError(EmojiError):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "Name Already Exists"

class EmojiFileExistsError(EmojiError):
    def __init__(self,
                 *args: object,
                 message: str = None,
                 message_args: Tuple = None,
                 file_name: str = None,
                 directory: str = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "File Already Exists"
        self.file_name = file_name
        self.directory = directory

class EmojiFileSaveError(EmojiError):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "File Save Error"

class EmojiFileTypeError(EmojiError):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "Invalid File Type"

class EmojiInvalidNameError(EmojiError):
    def __init__(self, *args: object, message: str = None, message_args: Tuple = None):
        super().__init__(*args, message=message, message_args=message_args)

        self.name = "Invalid Name"
