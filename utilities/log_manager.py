from enum import Enum
import logging
import sys
from logging import Logger, Formatter


CONSOLE_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG

# set up logging to file
logging.basicConfig(level=FILE_LOG_LEVEL,
                    format='%(asctime)s  |  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='rs3-items.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler(sys.stdout)
console.setLevel(CONSOLE_LOG_LEVEL)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

root_logger: Logger = logging.getLogger('')


# def get_console_handler():
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setFormatter(FORMATTER)
#     return console_handler
#
#
# def get_file_handler():
#     file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
#     file_handler.setFormatter(FORMATTER)
#     return file_handler
#
#
def get_logger(logger_name):
    # logger = logging.getLogger(logger_name)
    # logger.propagate = False

    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(CONSOLE_LOG_LEVEL)
    # console_handler.setFormatter(Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
    # logger.addHandler(console_handler)

    logger = root_logger.getChild(logger_name)

    return logger

# class LogLevel(Enum):
#     LOW = 1
#     MID = 2
#     HIGH = 3

# class Log:
#
#     level: LogLevel = LogLevel.LOW
#     """Specifies the amount of log info that will be printed to the console."""
#
#     # @classmethod
#     # def _log(cls, )
#
#     @classmethod
#     def error(cls, message: str):
#         """Prints error message to console regardless of log level."""
#         print(message)
