"""
Implementation of logging capabilities to be used by the master and slave
"""

from time import strftime
from enum import Enum

SET_PURPLE = '\033[95m'
SET_BLUE = '\033[94m'
SET_GREEN = '\033[92m'
SET_WARN = '\033[93m'
SET_ERROR = '\033[91m'
SET_END = '\033[0m'
SET_BOLD = '\033[1m'
SET_UNDERLINE = '\033[4m'

SEPARATOR = '========================================================'


class LogLevel(Enum):
    """
    Enumerated log levels
    """
    TRACE = 4
    DEBUG = 3
    INFO = 2
    WARN = 1
    ERROR = 0


class Logger:
    """
    Provides functionality to log errors, warnings, info, success, and debug
    """

    def __init__(self, log_level: LogLevel = LogLevel.TRACE):
        self.log_level = log_level.value
        # TODO: log_*() functions check log level before printing

    def log_error(self, message: str, end='\n'):
        """
        Logs error messages

        :param message: String - the message to log
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold(f'{SET_ERROR}ERROR', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def log_warn(self, message: str, end='\n'):
        """
        Logs warning messages

        :param message: String - the message to log
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        if self.log_level < LogLevel.WARN.value:
            return
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold(f'{SET_WARN}WARNING', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def log_info(self, message: str, end='\n'):
        """
        Logs info messages

        :param message: String  - the message to log
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        if self.log_level < LogLevel.INFO.value:
            return
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold(f'{SET_BLUE}INFO', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def log_success(self, message: str, header: str = 'SUCCESS', end='\n'):
        """
        Logs success messages

        :param message: String - the message to log
        :param header: String (optional) - string for the message header tag. Defaults to 'Success'
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        if self.log_level < LogLevel.INFO.value:
            return
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold(f'{SET_GREEN}{header}', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def log_debug(self, message: str, end='\n'):
        """
        Logs debug messages

        :param message: String - the message to log
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        if self.log_level < LogLevel.DEBUG.value:
            return
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold(f'{SET_PURPLE}DEBUG', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def log_trace(self, message: str, end='\n'):
        """
        Logs trace messages

        :param message: String - the message to log
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        if self.log_level < LogLevel.TRACE.value:
            return
        self.print_bold(f'\n{SEPARATOR}')
        self.print_bold('TRACE', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)
        self.print_bold(f'{SEPARATOR}')

    def print_datetime(self, end='\n'):
        """
        Prints the current date time in the following format
        [DD Mon YYYY - HH:MM:SS] ( ex: [08 Jun 2020 - 20:14:08])

        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        self.print_bold(
            f'[{strftime("%d %b %Y - %H:%M:%S")}]', end=end)

    @staticmethod
    def print_sameline(message: str):
        """
        **Meant to be called repeatedly**
        ie) in a loop

        :param message:
        :return:
        """
        print(f'\r{message}', end='')

    @staticmethod
    def print_bold(message: str, end='\n'):
        """
        **Meant for use internally**
        Prints the message in bold formatting

        :param message: String - the message to print
        :param end: String (optional) - string appended to the end of the message. Defaults to newline
        :return:
        """
        print(f'{SET_BOLD}{message}{SET_END}', end=end)


if __name__ == "__main__":
    logger = Logger(LogLevel.DEBUG)
    trace_logger = Logger()
    logger.log_error('error msg')
    logger.log_warn('warn msg')
    logger.log_info('info blue msg')
    logger.log_success('success msg')
    logger.log_debug('debug msg')
    logger.log_trace('shouldn\'t print unless log level set to TRACE')
    trace_logger.log_trace('trace msg')
