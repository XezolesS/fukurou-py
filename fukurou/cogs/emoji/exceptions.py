class EmojiError(Exception):
    pass

class EmojiDatabaseError(EmojiError):
    pass

class EmojiNameExistsError(EmojiError):
    pass

class EmojiFileExistsError(EmojiError):
    def __init__(self,
                 file_name: str = None,
                 directory: str = None,
                 *args):
        super().__init__(args)

        self.file_name = file_name
        self.directory = directory

class EmojiFileSaveError(EmojiError):
    pass

class EmojiFileTypeError(EmojiError):
    pass

class EmojiInvalidNameError(EmojiError):
    pass
