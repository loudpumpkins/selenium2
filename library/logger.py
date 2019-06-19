from config import *

# external
import logging
import inspect
from os.path import basename

# internal


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

	def __init__(self, debug=DEBUG):
		# Create a custom logger
		logger = logging.getLogger(self.get_caller_filename())
		logger.setLevel(logging.DEBUG) # minimum allowed level in root

		# Create handlers
		c_handler = logging.StreamHandler()
		f_handler = logging.FileHandler('library.log')
		f_handler.setLevel(logging.ERROR)
		if debug:
			c_handler.setLevel(logging.DEBUG)
		else:
			c_handler.setLevel(logging.INFO)

		# Create formatters and add it to handlers
		c_format = logging.Formatter('%(name)s::%(funcName)s::line %(lineno)d - %(levelname)s - %(message)s')
		f_format = logging.Formatter('%(asctime)s::%(name)s::%(funcName)s::line %(lineno)d - %(levelname)s - %(message)s', datefmt='%Y/%m/%d::%H/%M/%S')
		c_handler.setFormatter(c_format)
		f_handler.setFormatter(f_format)

		# Add handlers to the logger
		logger.addHandler(c_handler)
		logger.addHandler(f_handler)

		self.log = logger

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


class ElementNotFound(Exception):
	pass


class WindowNotFound(Exception):
	pass


class CookieNotFound(Exception):
	pass


class NoOpenBrowser(Exception):
	pass