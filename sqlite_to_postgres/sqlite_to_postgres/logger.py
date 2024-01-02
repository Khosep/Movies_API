import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils import create_dir_if_not_exists

LOGS_DIR = Path().resolve() / 'logs'
LOG_FILE = 'movies_db'
LOG_FILE_SIZE = 5 * 1024 * 1024

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

format = '[%(asctime)s][%(levelname)s][%(filename)s]<%(message)s>:' \
         'line:%(lineno)d|func:%(funcName)s'
file_log_format = '[%(asctime)s][%(levelname)s][%(filename)s]<%(message)s>:' \
                  'line:%(lineno)d|func:%(funcName)s|%(processName)s:%(threadName)s'

date_format = "%Y-%m-%d %H:%M:%S"
file_formatter = logging.Formatter(fmt=file_log_format, datefmt=date_format)
stream_formatter = logging.Formatter(fmt=format, datefmt=date_format)

create_dir_if_not_exists(LOGS_DIR)
file_handler = RotatingFileHandler(LOGS_DIR / LOG_FILE, maxBytes=LOG_FILE_SIZE, backupCount=5,
                                   encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(stream_formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
