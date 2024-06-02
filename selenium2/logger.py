import logging
import inspect
import os
from os.path import basename


class Logger:
    """ Main classed used throughout the project

    ==LEVEL==   Numeric value
    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0

    usage:
    self.log.info("message")

    """
    _loggers = {}

    @classmethod
    def get_logger(cls, name=None):
        if name is None:
            name = cls.get_caller_filename()
        if name in cls._loggers:
            return cls._loggers[name]
        else:
            # Create and configure a new logger
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)  # Base level for all logs

            # Create handlers with formatters
            c_handler = logging.StreamHandler()
            f_handler = logging.FileHandler('library.log')
            c_format = logging.Formatter(
                '%(name)s::%(funcName)s::line %(lineno)d - %(levelname)s - %(message)s')
            f_format = logging.Formatter(
                '%(asctime)s::%(name)s::%(funcName)s::line %(lineno)d - %(levelname)s - %(message)s',
                datefmt='%Y/%m/%d::%H/%M/%S')

            if os.environ.get('SELENIUM2_DEBUG', True):
                c_handler.setFormatter(c_format)
            f_handler.setFormatter(f_format)
            logger.addHandler(c_handler)
            logger.addHandler(f_handler)
            cls._loggers[name] = logger
            return logger

    @staticmethod
    def get_caller_filename():
        # get the caller's stack frame and extract its filename
        frame_info = inspect.stack()[2]     # go 2 stacks down : get_caller_filename > Logger.__init__ > calling file
        path = frame_info.filename
        filename = basename(path)
        if len(filename) < 3:
            # return entire path in case of failed filename extraction
            return path
        else:
            return filename