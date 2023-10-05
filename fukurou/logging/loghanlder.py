import os
from datetime import datetime

from fukurou.configs import configs

class LogHandler:
    """
        A class for handling log files.
    """

    @property
    def directory(self) -> str:
        """
            The directory that logs to be stored.
        """
        return self.__directory

    @property
    def max_logs(self) -> int:
        """
            Maximum number of logs to be stored.
        """
        return self.__max_logs

    @property
    def name_format(self) -> str:
        """
            Format string of the log file name.
        """
        return self.__name_format

    @property
    def time_format(self) -> str:
        """
            Format string of the time for log file name.
        """
        return self.__time_format

    def __init__(self):
        log_config = configs.get_config('logging')
        self.__directory = log_config.directory
        self.__max_logs = log_config.max_logs
        self.__name_format = log_config.file_name
        self.__time_format = log_config.file_time

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
        # Create log file
        time = datetime.now()
        file_name = self.name_format % { 'datetime': time.strftime(self.time_format) }
        file_path = os.path.join(self.directory, file_name + '.log')

        open(file=file_path, mode='x', encoding='utf-8')

        # Remove log file if max log count exceeded.
        while len(self.__logs) >= self.max_logs:
            oldest = min(self.__logs, key=os.path.getctime)

            self.__logs.remove(oldest)
            os.remove(oldest)

        return file_path
