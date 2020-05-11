import logging
from .config import LOG_LEVEL, LOG_FILE

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# create handler for logging to file
fileHandler = logging.FileHandler(LOG_FILE)
fileHandler.setLevel(LOG_LEVEL)

# create log formatter
formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')

# add the formatter to the handler
fileHandler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(fileHandler)