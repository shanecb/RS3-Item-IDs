import logging
import sys
from logging import Logger


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


def get_logger(logger_name):
    return root_logger.getChild(logger_name)
