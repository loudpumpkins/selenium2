from .config import *

# external

# internal
from .logger import Logger
from .browser_support.alert import Alert
from .browser_support.browsermanagement import BrowserManagement
from .browser_support.element import Element
from .browser_support.frames import Frames
from .browser_support.javascript import Javascript
from .browser_support.screenshot import Screenshot
from .browser_support.selects import Selects
from .browser_support.tables import Tables
from .browser_support.waiting import Waiting
from .browser_support.windowmanager import WindowManager
from .browser_support._webdrivercreator import WebDriverCreator


class Browser:
	"""
	Selenium Webdriver Controller
	Uses WebDriverCreator to make a browser and mixins for support
	functionality.

	See browser.pyi for all function prototypes available to Browser.
	More detailed documentation coming soon, but each individual function is
	documented in their respected file.

	=== WebDriverCreator ===

	supported browser: 'firefox', 'headless firefox', 'headless chrome',
	'chrome', 'ie', 'edge'. NOTE: avoid using options and profiles if possible
	as they will be deprecated.

	Instantiating a new browser example:
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

	=== Available methods ===

	A browser instance will have all the methods not pre-fixed with an
	underscore (_) defined the following classes / files:

			Driver              |   _driver.py
			Base                |   _base.py
			Alert               |   alert.py
			BrowserManagement   |   browsermanagement.py
			Element             |   element.py
			Frames              |   frames.py
			Javascript          |   javascript.py
			Screenshot          |   screenshot.py
			Selects             |   selects.py
			Tables              |   tables.py
			Waiting             |   waiting.py
			WindowManager       |   windowmanager.py


	"""

	def __init__(self, browser='ff', desired_capabilities=None,
	             profile=None, options=None):
		self.driver = WebDriverCreator().create_driver(
			browser, desired_capabilities, profile, options
		)
		self.implicit_wait = 0
		self.log = Logger().log
		self.speed = DEFAULT_SPEED # TODO add a session speed controller
		self.timeout = DEFAULT_TIMEOUT
		self.screenshot_directory = SCREENSHOT_ROOT_DIRECTORY
		libraries = [
			Alert(self),
			BrowserManagement(self),
			Element(self),
			Frames(self),
			Javascript(self),
			Screenshot(self),
			Selects(self),
			Tables(self),
			Waiting(self),
			WindowManager(self),
		]
		self.get_attributes(libraries)

	def __enter__(self):
		# python context manager
		return self

	def __exit__(self, *args):
		# python context manager
		self.quit()

	# TODO possibly add a session manager to allow for multiple sessions at once
	# @property
	# def driver(self):
	# 	return self.driver
	#
	# @driver.setter
	# def driver(self, driver):
	# 	self.driver = driver

	def get_attributes(self, libraries):
		"""	Will parse every method in ``libraries`` and append those that
		don't start with an underscore (_) to `self`.

		All methods defined in ``libraries`` that start with an underscore are
		considered `helper methods` to `core methods` and should not be used
		directly by `self`, hence, are omitted.

		This also applied to attributes.
		"""
		for library in libraries:
			for name, value in self.get_members(library):
				if not hasattr(self, name) and not name.startswith('_'):
				# avoid overwriting existing attributes and exclude _named attributes
					setattr(self, name, value)

	def get_members(self, library):
		"""Get the name:value pairs of the methods in the instance provided."""
		for name in dir(library):
			yield name, getattr(library, name)

	def set_implicit_wait(self, time_to_wait):
		self.driver.implicitly_wait(time_to_wait)
		self.implicit_wait = time_to_wait

	def unset_implicit_wait(self):
		self.driver.implicitly_wait(0)
		self.implicit_wait = 0




