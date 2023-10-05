import os
from datetime import datetime

class LogHandler:
    """
        A class for handling log files.
    """

    @property
    def directory(self) -> str:
        """
            The directory that logs to be stored.
        """
        return 'logs'

    @property
    def max_logs(self) -> int:
        """
            Maximum number of logs to be stored.
        """
        return 10

    @property
    def name_format(self) -> str:
        """
            Format string of the log file name.
        """
        return '%(datetime)s_fukurou'

    @property
    def time_format(self) -> str:
        """
            Format string of the time for log file name.
        """
        return "%Y-%m-%d_%H.%M.%S"

    def __init__(self):
        # Create log directory if it doesn't exist.
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # List all logs in the directory
        files = os.listdir(self.directory)
        self.__logs = [
            os.path.join(self.directory, f) for f in files
            if os.path.isfile(os.path.join(self.directory, f))
            and f.endswith(".log")
        ]

    def create_next(self) -> str:
        """
            Create the log file which satisfies the format.
            Delete oldest log file when max log count exceeded.

            :return: Path of the created log file
            :rtype: str
        """
        # Remove log file if max log count exceeded.
        if len(self.__logs) == self.max_logs:
            oldest = min(self.__logs, key=os.path.getctime)
            os.remove(oldest)

        time = datetime.now()
        file_name = self.name_format % { 'datetime': time.strftime(self.time_format) }
        file_path = os.path.join(self.directory, file_name + '.log')

        open(file=file_path, mode='x', encoding='utf-8')

        return file_path
