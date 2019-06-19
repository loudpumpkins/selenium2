from config import *

# external
from selenium import webdriver

# internal
from .logger import Logger
from .browser_support.alert import Alert
from .browser_support.browsermanagement import BrowserManagement
from .browser_support.element import Element
from .browser_support.methodsmixin import MethodsMixin
from .browser_support.webdrivercreator import WebDriverCreator



class Browser:
	"""

	Selenium Webdriver Controller
	Uses WebDriverCreator to make a browser and mixins for support
	functionality.

	=== WebDriverCreator ===

	supported 'firefox', 'headless firefox', 'headless chrome',
	'chrome', 'ie', 'edge'. NOTE: avoid using options and profiles if possible
	as they will be deprecated.

	usage:
	-   basic browser:
			chrome = Browser('chrome')
	-   with desired capabilities
			proxy = {
				'proxyType':'manual',
				'httpProxy':'25.25.125.125:8080',
			}
			dc = {
				'proxy':proxy,
			}
			firefox = Browser('firefox', desired_capabilities=dc)

	=== MethodsMixin

	"""

	def __init__(self, browser='ff', desired_capabilities=None,
	             profile=None, options=None):
		self.log = Logger().log
		self.timeout = DEFAULT_TIMEOUT
		self.implicit_wait = DEFAULT_IMPLICIT_WAIT
		self.speed = DEFAULT_SPEED
		self.driver = WebDriverCreator().create_driver(
			browser, desired_capabilities, profile, options
		)
		libraries = [
			Alert(self),
			BrowserManagement(self),
			Element(self),
			MethodsMixin(self),
		]
		self.get_attributes(libraries)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.driver.quit()

	# @property
	# def driver(self):
	# 	return self.driver
	#
	# @driver.setter
	# def driver(self, driver):
	# 	self.driver = driver

	def get_attributes(self, libraries):
		for library in libraries:
			for name, value in self.get_members(library):
				if not hasattr(self, name) and not name.startswith('_'):
				# avoid overwriting existing attributes and exclude _named attributes
					setattr(self, name, value)

	def get_members(self, library):
		for name in dir(library):
			yield name, getattr(library, name)




