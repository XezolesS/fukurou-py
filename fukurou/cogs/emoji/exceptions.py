class EmojiError(Exception):
    """
    General Emoji error.
    """

class EmojiCapacityExceededError(EmojiError):
    """
    Raise if the number of Emojis in the guild reaches it's capacity limit.

    `*args` contains:
    - `[0]`: Capacity limit.
    """

class EmojiDatabaseError(EmojiError):
    """
    Raise if database operation failed.
    """

class EmojiExistsError(EmojiError):
    """
    Raise if the Emoji already exists in the database.
    
    `*args` contains:
    - `[0]`: Name of the Emoji.
    - `[1]`: Name of the Emoji file.
    """

class EmojiFileDownloadError(EmojiError):
    """
    Raise if the file cannot be downloaded.
    """

class EmojiFileExistsError(EmojiError):
    """
    Raise if the file already exists in the storage.

    `*args` contains:
    - `[0]`: Name of the Emoji that corresponds with the file.
    """

class EmojiFileIOError(EmojiError):
    """
    Raise if an error occured while reading/writing file.

    `*args` contains:
    - `[0]`: I/O operation that failed. `r`: reading, `w`: writing
    """

class EmojiFileTooLargeError(EmojiError):
    """
    Raise if the file is larger than the limit.

    `*args` contains:
    - `[0]`: Size of the file in KB.
    - `[1]`: Size limit in KB.
    """

class EmojiFileTypeError(EmojiError):
    """
    Raise if the file is not appropriate for the Emoji.

    `*args` contains:
    - `[0]`: Type of the file.
    """

class EmojiInvalidNameError(EmojiError):
    """
    Raise if the name of an Emoji is not in the valid format.
    
    `*args` contains:
    - `[0]`: Name of the Emoji.
    - `[1]`: Valid format in regular expression.
    """

class EmojiNotFoundError(EmojiError):
    """
    Raise if the Emoji is not found in the database.

    `*args` contains:
    - `[0]`: Name of the Emoji.
    """

class EmojiNotReadyError(EmojiError):
    """
    Raise if some required service for Emoji to run is not ready.

    `*args` contains:
    - `[0]`: Name of the unavaiable service.
    """
