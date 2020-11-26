import logging
import sys
from logging import Logger


CONSOLE_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG


logging.basicConfig(level=FILE_LOG_LEVEL,
                    format='%(asctime)s  |  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='rs3-items.log',
                    filemode='w')


root_logger: Logger = logging.getLogger('')


# add another handler to root logger so we can get log messages sent to stout in addition to log file
console = logging.StreamHandler(sys.stdout)
console.setLevel(CONSOLE_LOG_LEVEL)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
root_logger.addHandler(console)


def get_logger(logger_name):
    return root_logger.getChild(logger_name)
