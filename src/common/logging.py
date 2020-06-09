from enum import Enum
from time import strftime


SET_PURPLE = '\033[95m'
SET_BLUE = '\033[94m'
SET_GREEN = '\033[92m'
SET_WARN = '\033[93m'
SET_ERROR = '\033[91m'
SET_END = '\033[0m'
SET_BOLD = '\033[1m'
SET_UNDERLINE = '\033[4m'

SEPARATER = '*****************************************'


class Logger:

    def log_error(self, message: str, end='\n'):
        self.print_bold(f'{SEPARATER}')
        self.print_bold(f'{SET_ERROR}ERROR', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)

    def log_warn(self, message: str, end='\n'):
        self.print_bold(f'{SEPARATER}')
        self.print_bold(f'{SET_WARN}WARNING', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)

    def log_info(self, message: str, end='\n'):
        self.print_bold(f'{SEPARATER}')
        self.print_bold(f'{SET_BLUE}INFO', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)

    def log_success(self,  message: str, header:str = 'SUCCESS', end='\n'):
        self.print_bold(f'{SEPARATER}')
        self.print_bold(f'{SET_GREEN}{header}', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)

    def log_debug(self, message: str, end='\n'):
        self.print_bold(f'{SEPARATER}')
        self.print_bold(f'{SET_PURPLE}DEBUG', end=' ')
        self.print_datetime(end='')
        print(f':\n{message}', end=end)

    def print_datetime(self, end='\n'):
        self.print_bold(
            f'[{strftime("%d %b %Y - %H:%M:%S")}]{SET_END}', end=end)

    def print_bold(self, message: str, end='\n'):
        print(f'{SET_BOLD}{message}{SET_END}', end=end)

    def test_colours(self):
        print(f'{SET_PURPLE}PURPLE{SET_END} ', end='')
        print(f'{SET_BLUE}BLUE{SET_END} ', end='')
        print(f'{SET_GREEN}GREEN{SET_END} ', end='')
        print(f'{SET_WARN}WARN{SET_END} ', end='')
        print(f'{SET_ERROR}ERROR{SET_END} ', end='')
        print(f'{SET_BOLD}BOLD{SET_END} ', end='')
        print(f'{SET_UNDERLINE}UNDERLINE{SET_END}')


if __name__ == "__main__":

    logger = Logger()
    logger.test_colours()
    logger.log_error('error msg')
    logger.log_warn('warn msg')
    logger.log_info('info blue msg')
    logger.log_success('success msg')
    logger.log_debug('test')
