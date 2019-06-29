from config import *

# external
from selenium.webdriver.remote.webdriver import WebDriver

# internal
from ..logger import Logger


class Driver:

	def __init__(self, root):
		"""
		The root class which holds the global browser driver.
		:param root:
		"""
		self._root = root
		self.log = Logger().log

	@property
	def driver(self):
		driver: WebDriver = self._root.driver
		return driver