from .config import *

# external
import re

# internal
from .logger import Logger
from .browser_support.alert import Alert
from .browser_support.browsermanagement import BrowserManagement
from .browser_support.cookies import Cookies
from .browser_support.element import Element
from .browser_support.frames import Frames
from .browser_support.javascript import Javascript
from .browser_support.screenshot import Screenshot
from .browser_support.selects import Selects
from .browser_support.tables import Tables
from .browser_support.waiting import Waiting
from .browser_support.windowmanager import WindowManager
from .browser_support._webdrivercreator import WebDriverCreator
from .site_specific import DefaultBehaviour, Kijiji


class Browser:
	"""
	Selenium Webdriver Controller
	Uses WebDriverCreator to make a browser and mixins for support
	functionality found in ./browser_support.

	See browser.pyi for all function prototypes available to Browser.
	More detailed documentation coming soon, but each individual function is
	documented in their respective files.

	=== WebDriverCreator ===

	WebDriverCreator, found in ./browser_support/_webdrivercreator.py, will
	start a new session with the browser of choice provided when instantiating
	"Browser" at it's first function argument, "browser=". Firefox is the
	default browser if none is specified.

	Supported browsers: 'firefox', 'headless firefox', 'headless chrome',
	'chrome', 'ie', 'edge'. NOTE: avoid using options and profiles if possible
	as they will be deprecated by selenium.

	Browser.__init__() arguments:
		:param browser: A string representing the desired browser from the list
			`supported browsers` above. `browser` is case insensitive and
			aliases are available such as "ff" for "firefox". See
			_webdrivercreator.py -> "browser_names" for all aliases.
		:param desired_capabilities: Dictionary object with non-browser specific
			capabilities only, such as "proxy" or "loggingPref".
			list: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities
		:param profile: Instance of ``FirefoxProfile`` object or a string.
			If undefined, a fresh profile will be created in a temporary
			location on the system. (Firefox exclusive argument)
		:param options: this takes an instance of browser specific options class
			such as webdriver.FirefoxOptions()

	Examples:

	-   basic browser:
			chrome = Browser('chrome')

	-   with proxy:
			proxy = {
				'proxyType': 'MANUAL',
				'sslProxy': '192.0.0.1:80',
				'httpProxy': '192.0.0.1:80',
				'ftpProxy': '192.0.0.1:80',
			}
			dc = {
				'proxy': proxy,
			}
			firefox = Browser('firefox', desired_capabilities=dc)

	-   with anonymity:
			profile = FirefoxProfile()
			profile.set_preference("dom.webdriver.enabled", False)
			profile.set_preference('useAutomationExtension', False)
			profile.update_preferences()

			firefox = Browser('firefox', profile=profile)

	NOTE: browser specific drivers need to be present and their path
	needs to be appended in the system's PATH variable.
	DOWNLOAD LINK: https://www.seleniumhq.org/download/

	=== Available methods ===

	A browser instance will have all the methods not pre-fixed with an
	underscore (_) defined in the following classes/files:

		_____CLASS_NAME_________|____FILE_NAME______________|___HIERARCHY_____
			Driver              |   _driver.py              |   parent
			Base                |   _base.py                |   child
			Alert               |   alert.py                |   leaf
			BrowserManagement   |   browsermanagement.py    |   leaf
			Cookies             |   cookies.py              |   leaf
			Element             |   element.py              |   leaf
			Frames              |   frames.py               |   leaf
			Javascript          |   javascript.py           |   leaf
			Screenshot          |   screenshot.py           |   leaf
			Selects             |   selects.py              |   leaf
			Tables              |   tables.py               |   leaf
			Waiting             |   waiting.py              |   leaf
			WindowManager       |   windowmanager.py        |   leaf

	=== Additional functionality ===

	Additional site-specific methods are available, but a site must be set first.
	This ca be done using ``Browser.set_site_behaviour(sitename)``

	For instance, before you can use 'sign_in' or 'create_account', you must indicate
	for which site you would like this behaviour to occur.

	Example:

		chrome = Browser('chrome')

		chrome.set_site_behaviour('facebook')
		chrome.sign_in(credentials)
		chrome.post_content(details)
		chrome.sign_out()

		chrome.set_site_behaviour('kijiji')
		chrome.sign_in(credentials)
		chrome.post_content(ad)
		chrome.sign_out()

	"""

	def __init__(self, browser='ff', desired_capabilities=None,
	             profile=None, options=None):
		self.driver = WebDriverCreator().create_driver(
			browser, desired_capabilities, profile, options
		)
		self.implicit_wait = 0
		self.log = Logger().log
		self.speed = DEFAULT_SPEED  # TODO add a session speed controller
		self.timeout = DEFAULT_TIMEOUT
		self.screenshot_directory = SCREENSHOT_ROOT_DIRECTORY
		self.cookies_directory = COOKIES_ROOT_DIRECTORY
		libraries = [
			Alert(self),
			BrowserManagement(self),
			Cookies(self),
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
		self.site_specific_behaviour = DefaultBehaviour(self)

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

	def set_site_behaviour(self, site):
		"""
		Set site-specific behaviour to the given site.
		For instance, before you can use 'sign_in' or 'create_account', you must
		indicate for which site you would like this behaviour to occur.

		The following are site-specific methods which require a site to be set
		first.

			def create_account(self, details: dict, cookies: str = None): ...
			def is_signed_in(self) -> bool: ...
			def is_signed_out(self) -> bool: ...
			def post(self, details: dict) -> str: ...
			def sign_in(self, details: dict, cookies: str = None) -> NoReturn: ...
			def sign_out(self) -> NoReturn: ...
		"""
		sites = {
			'kijiji': Kijiji,
			'default': DefaultBehaviour,
		}
		if site.lower() not in sites:
			raise NotImplemented('No behaviour found for the given site: %s.' % site)
		self.site_specific_behaviour = sites[site.lower()](self)

	def create_account(self, details: dict, cookies: str = None):
		"""
		Create an account for the site using the credentials found in `details`.
		If a `cookies` filename is provided, it will save the cookies after creating
		an account.

		:return: bool - True for success
		"""
		return self.site_specific_behaviour.create_account(details, cookies)

	def create_content(self, details: dict) -> str:
		"""
		Post an ad, a tweet, a post, an image, etc. The main purpose of the
		site that we are building behaviour for.

		:return: str - returns an identifier to the new content (url, ID, ...)
		"""
		return self.site_specific_behaviour.create_content(details)

	def delete_content(self, details: dict) -> bool:
		"""
		Delete an ad, a tweet, a post, an image, etc. The main purpose of the
		site that we are building behaviour for.

		:return: bool - returns True if content found and delete. False otherwise.
		"""
		return self.site_specific_behaviour.delete_content(details)

	def edit_content(self, details: dict) -> bool:
		"""
		Edit an ad, a tweet, a post, an image, etc. The main purpose of the
		site that we are building behaviour for.

		:return: bool - returns True of content found and edited. False otherwise.
		"""
		return self.site_specific_behaviour.edit_content(details)

	def is_signed_in(self):
		"""
		Explicitly assert that user is logged in. Does not rely on 'is_signed_out'.

		:return: bool - True for logged in
		"""
		return self.site_specific_behaviour.is_signed_in()

	def is_signed_out(self):
		"""
		Explicitly assert that user is logged out. Does not rely on 'is_signed_in'.

		:return: bool - True for logged out
		"""
		return self.site_specific_behaviour.is_signed_out()

	def sign_in(self, details, cookies=None):
		"""
		Sign in to the site using the credentials found in `details`.
		If a `cookies` filename is provided, it will try to load it and see if
		the user is now logged in.
		If the `cookies` filename is not found, it will try to sign in normally
		and save the `cookies` file after signing in.
		"""
		self.site_specific_behaviour.sign_in(details, cookies)

	def sign_out(self):
		"""
		Sign out from the site. Will try assert that sign_out() was successful.
		"""
		self.site_specific_behaviour.sign_out()

	def site_custom(self, method_name, *args):
		"""
		Once a site_specific_behaviour is set, you may call a custom method
		available only to the specific site.

		:param method_name: name of the method to call
		:param args: arguments to pass to the method
		"""
		if hasattr(self.site_specific_behaviour, method_name):
			method = getattr(self.site_specific_behaviour, method_name)
			if callable(method):
				return method(*args)
			else:
				raise RuntimeError("Attribute `%s` of site `%s` is not callable."
							% (method_name, self.site_specific_behaviour.name))
		else:
			raise RuntimeError("Site `%s` does not have an attribute named `%s`."
							% (self.site_specific_behaviour.name, method_name))

	def get_attributes(self, libraries):
		"""
		Will parse every method in ``libraries`` and append those that
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

	def assert_proxy_is(self, ip):
		"""
		Use the created driver to navigate to ip-secrets.com and confirm that
		the ``ip`` provided is the one currently used. Will test for `https`
		and `http` page requests.
		:param ip: str - the proxy expected to be running traffic through
		:return: NoReturn
		"""
		groups = re.search(r'^(\d+\.\d+\.\d+\.\d+):?(\d+)?', ip)
		if groups is None:
			raise ValueError(
				'The proxy addess provided ({}) is not a valid address.'.format(
					ip))
		else:
			ip_address = groups.group(1)
			# port = groups.group(2) #port not used for the verification
		self.driver.get('https://www.ip-secrets.com/')
		page_source = self.driver.page_source
		if ip_address not in page_source:
			raise AssertionError('The provided IP address ({}) is not set '
			                     'for ssl page requests.'.format(ip_address))
		self.log.info('Proxy (%s) passed the ssl page requests test.' % ip)
		self.driver.get('http://www.ip-secrets.com/')
		page_source = self.driver.page_source
		if ip_address not in page_source:
			raise AssertionError('The provided IP address ({}) is not set '
			                     'for http page requests.'.format(ip_address))
		self.log.info('Proxy (%s) passed the http page requests test.' % ip)

	def set_implicit_wait(self, time_to_wait):
		"""
		Set the time in seconds for the driver to wait for pages/elements.
		This is implemented by the browser's driver and not selenium. As a
		result, behaviour can be unexpected as it is barely documented and
		each browser might have different implementations.

		Recommend using explicit waits or the wait functions in `waiting.py`

		:param time_to_wait: int - time to wait in seconds
		:return: NoReturn
		"""
		self.driver.implicitly_wait(time_to_wait)
		self.implicit_wait = time_to_wait

	def unset_implicit_wait(self):
		"""Sets implicit_wait to 0, effectively disabling it."""
		self.driver.implicitly_wait(0)
		self.implicit_wait = 0




