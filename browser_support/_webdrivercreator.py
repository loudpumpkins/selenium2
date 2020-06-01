from ..config import *

# external
from selenium import webdriver

# internal
from ..logger import Logger


class WebDriverCreator:
	"""
	Solely responsible for creating a web driver for the specified browser with
	the desired capabilities and options. Used in browser.py.

	Usage: driver = WebDriverCreator().create_driver(
				browser, desired_capabilities, profile, options
			)
	"""

	browser_names = {
		# chrome
		'googlechrome':'chrome', 'gc':'chrome', 'chrome':'chrome', 'google':'chrome',
		# ninja chrome - anti robot detection browser in chrome
		'ninja':'ninja', 'hidden':'ninja', 'secret':'ninja',
		'ninja chrome':'ninja', 'hidden chrome':'ninja', 'secret chrome':'ninja',
		'ninja-chrome':'ninja', 'hidden-chrome':'ninja', 'secret-chrome':'ninja',
		'ninja_chrome':'ninja', 'hidden_chrome':'ninja', 'secret_chrome':'ninja',
		# headless chrome
		'headlesschrome':'headless_chrome', 'chromeheadless':'headless_chrome',
		'headless_chrome':'headless_chrome', 'headless chrome':'headless_chrome',
		# firefox
		'ff':'firefox', 'firefox':'firefox',
		# headless firefox
		'headlessfirefox':'headless_firefox', 'firefoxheadless':'headless_firefox',
		'headless firefox':'headless_firefox', 'headless_firefox':'headless_firefox',
		# internet explorer
		'ie':'ie', 'internetexplorer':'ie', 'explorer':'ie',
		# edge
		'edge':'edge',

		# TODO: add other browsers
		# 'opera' : 'opera',
		# 'safari' : 'safari',
		# 'phantomjs' : 'phantomjs',
		# 'htmlunit' : 'htmlunit',
		# 'htmlunitwithjs' : 'htmlunit_with_js',
		# 'android' : 'android',
		# 'iphone' : 'iphone'
	}


	def __init__(self):
		self.log = Logger().log

	def create_driver(self, browser, desired_capabilities=None, profile=None, options=None):
		"""
		Main function that will make the browser's driver
		:param browser: A string representing the desired browser
		:param desired_capabilities: Dictionary object with non-browser specific
            capabilities only, such as "proxy" or "loggingPref".
            list: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities
		:param profile: Instance of ``FirefoxProfile`` object or a string.  If undefined,
			a fresh profile will be created in a temporary location on the system.
		:param options: this takes an instance of browser specific options class
			such as webdriver.FirefoxOptions()
		:return: browser controlling driver
		"""
		creation_method = self.get_creation_method(browser)

		return creation_method(desired_capabilities, profile, options)

	def get_creation_method(self, browser):
		"""
		Fetch browser specific creation method required by create_driver() method
		:param browser: A string representing the desired browser
		:return: driver creation method
		"""
		browser = browser.lower()
		if browser in self.browser_names:
			return getattr(self, 'create_{}'.format(self.browser_names[browser]))
		raise ValueError('{} is not a supported browser yet.\n'
		        'Available: chrome, firefox, headless chrome, headless firefox, '
		        'explorer and edge.'.format(browser))

	###############################################
	### browser specific creation methods below ###
	###############################################

	def create_chrome(self, desired_capabilities, profile, options):
		if profile is not None:
			self.log.warning('Chrome was instantiated with a profile which is a '
			                 'firefox exclusive parameter.')
		if desired_capabilities is not None:
			default_desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
			default_desired_capabilities.update(desired_capabilities)
			desired_capabilities = default_desired_capabilities
		else:
			desired_capabilities = {}
		return webdriver.Chrome(desired_capabilities=desired_capabilities, options=options)

	def create_ninja(self, desired_capabilities, profile, options):
		"""
		Recommended to edit chromedriver.exe by replacing all 'cdc_' text to
		'dog_' or anything else. Also, `Options` argument is ignored.
		"""
		if profile is not None:
			self.log.warning('Chrome was instantiated with a profile which is a '
			                 'firefox exclusive parameter.')
		if options is not None:
			self.log.warning('Chrome ninja comes with preset options, but additional '
			                 'options were provided.')
		options = webdriver.ChromeOptions()
		options.add_experimental_option("excludeSwitches",
		                                ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		if desired_capabilities is not None:
			default_desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
			default_desired_capabilities.update(desired_capabilities)
			desired_capabilities = default_desired_capabilities
		else:
			desired_capabilities = {}

		driver = webdriver.Chrome(desired_capabilities=desired_capabilities, options=options)
		driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
			"source": """
		    Object.defineProperty(navigator, 'webdriver', {
		      get: () => undefined
		    })
		  """
		})
		driver.execute_cdp_cmd("Network.enable", {})
		driver.execute_cdp_cmd("Network.setExtraHTTPHeaders",
		                       {"headers": {"User-Agent": "browser1"}})
		return driver

	def create_headless_chrome(self, desired_capabilities, profile, options):
		if profile is not None:
			self.log.warning('Chrome was instantiated with a profile which is a firefox exclusive parameter.')
		if options is None:
			options = webdriver.ChromeOptions()
		options.headless = True
		return self.create_chrome(desired_capabilities, profile, options)

	def create_firefox(self, desired_capabilities, profile, options):
		if desired_capabilities is not None:
			default_desired_capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
			default_desired_capabilities.update(desired_capabilities)
			desired_capabilities = default_desired_capabilities
		else:
			desired_capabilities = {}
		return webdriver.Firefox(desired_capabilities=desired_capabilities, firefox_profile=profile, options=options)

	def create_headless_firefox(self, desired_capabilities, profile, options):
		if options is None:
			options = webdriver.FirefoxOptions()
		options.headless = True
		return self.create_firefox(desired_capabilities, profile, options)

	def create_ie(self, desired_capabilities, profile, options):
		if profile is not None:
			self.log.warning('IE was instantiated with a profile which is a firefox exclusive parameter.')
		if desired_capabilities is not None:
			default_desired_capabilities = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
			default_desired_capabilities.update(desired_capabilities)
			desired_capabilities = default_desired_capabilities
		else:
			desired_capabilities = {}
		return webdriver.Ie(desired_capabilities=desired_capabilities, options=options)

	def create_edge(self, desired_capabilities, profile, options):
		if profile is not None:
			self.log.warning('Edge was instantiated with a profile which is a firefox exclusive parameter.')
		if options is not None:
			self.log.warning('Edge was instantiated with options which is not allowed.')
		if desired_capabilities is not None:
			default_desired_capabilities = webdriver.DesiredCapabilities.EDGE.copy()
			default_desired_capabilities.update(desired_capabilities)
			desired_capabilities = default_desired_capabilities
		else:
			desired_capabilities = {}
		return webdriver.Edge(capabilities=desired_capabilities)

	###############################################
	###                   END                   ###
	###############################################