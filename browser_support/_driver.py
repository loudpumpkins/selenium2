from ..config import *

# external
from selenium.webdriver.remote.webdriver import WebDriver

# internal
from ..logger import Logger


class Driver:
	"""
	self._root is basically the 'Browser' class and self.driver refers to
	self._root.driver which is Browser.driver.
	"""

	def __init__(self, root):
		"""
		The root class which holds the global browser driver.
		:param root:
		"""
		self._root = root
		self.log = Logger().log

	@property
	def driver(self):
		"""
		`root` function argument is an instance of Browser.
		This is a @property as the Browser's `driver` will also be a @property
		with a driver manager (multiple drivers) in future updates.
		:return: WebDriver (current active driver)
		"""
		driver: WebDriver = self._root.driver
		return driver