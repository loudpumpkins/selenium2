from selenium import webdriver
from selenium.webdriver import ChromeOptions, FirefoxOptions, FirefoxProfile
from selenium.webdriver.safari.options import Options as SafariOptions

from ..logger import Logger


class WebDriverCreator:
    """
    Solely responsible for creating a web driver for the specified browser with
    the desired capabilities and options. Used in browser.py.

    Usage: driver = WebDriverCreator().create_driver(
                browser, desired_capabilities, profile, options
            )
    """

    def __init__(self):
        self.log = Logger.get_logger()

    def browser_name(self, browser):
        mapper = {
            # chrome
            'chrome': ['googlechrome', 'gc', 'chrome', 'google'],
            # ninja chrome - anti robot detection browser in chrome
            'chrome_ninja': [d.join(pair)
                             for d in (' ', '-', '_',)
                             for kw in ('ninja', 'incognito', 'private')
                             for pair in ((kw, 'chrome',), ('chrome', kw))],
            # headless chrome
            'headless_chrome': ['headlesschrome', 'chromeheadless',
                                'headless_chrome', 'headless chrome'],
            # firefox
            'firefox': ['ff', 'firefox'],
            # ninja ff - anti robot detection browser in firefox
            'firefox_ninja': [d.join(pair)
                              for d in (' ', '-', '_',)
                              for kw in ('ninja', 'incognito', 'private')
                              for ff in ('ff', 'firefox')
                              for pair in ((kw, ff,), (ff, kw))],
            # headless firefox
            'headless_firefox': ['headlessfirefox', 'firefoxheadless',
                                 'headless firefox', 'headless_firefox'],
            # internet explorer
            'ie': ['ie', 'ei', 'internetexplorer', 'explorer'],
            # edge
            'edge': ['edge'],
            'safari': ['safari'],

            # TODO: add other browsers
            # 'opera' : 'opera',
            # 'phantomjs' : 'phantomjs',
            # 'htmlunit' : 'htmlunit',
            # 'htmlunitwithjs' : 'htmlunit_with_js',
            # 'android' : 'android',
            # 'iphone' : 'iphone'
        }
        for key, value in mapper.items():
            if browser in value:
                return key

        raise ValueError(f'`{browser}` is not a supported browser yet.\n'
                         f'Available: {mapper.keys()}')

    def create_driver(self, browser, profile=None, options=None, ip=None):
        """
        Main function that will make the browser's driver
        :param browser: A string representing the desired browser
        :param profile: Instance of ``FirefoxProfile`` object or a string.  If undefined,
            a fresh profile will be created in a temporary location on the system.
        :param options: this takes an instance of browser specific options class
            such as webdriver.FirefoxOptions()
        :param ip: A string representing the ip address and port number
        :return: browser controlling driver
        """
        creation_method = self.get_creation_method(browser)
        return creation_method(profile, options, ip)

    def get_creation_method(self, browser):
        """
        Fetch browser specific creation method required by create_driver() method
        :param browser: A string representing the desired browser
        :return: driver creation method
        """
        return getattr(self, f'create_{self.browser_name(browser.lower())}')

    ############################################################################
    # browser specific creation methods

    def create_chrome(self, profile, options, ip):
        if profile is not None:
            self.log.warning('Chrome was instantiated with a profile which is a '
                             'firefox exclusive parameter.')
        if not options:
            options = ChromeOptions()
        if ip:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Chrome(options=options)

    def create_chrome_ninja(self, profile, options, ip):
        """
        Recommended to edit chromedriver.exe by replacing all 'cdc_' text to
        'dog_' or anything else.
        """
        if not options:
            options = ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = self.create_chrome(profile, options, ip)
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

    def create_headless_chrome(self, profile, options, ip):
        if options is None:
            options = webdriver.ChromeOptions()
        options.headless = True
        return self.create_chrome(profile, options, ip)

    def create_firefox(self, profile, options, ip):
        if not options:
            options = FirefoxOptions()
        if profile:
            profile_instance = FirefoxProfile(profile) if isinstance(profile, str) else profile
            options.profile = profile_instance
        if ip is not None:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Firefox(options=options)

    def create_firefox_ninja(self, profile, options, ip):
        """
        Sets up a 'ninja' profile for Firefox to avoid detection.
        """
        if profile is not None:
            self.log.warning('Firefox ninja received a `profile` which will be '
                             'ignored and replaced by `ninja profile`.')
        if not options:
            options = webdriver.FirefoxOptions()
        ninja_profile = FirefoxProfile()
        ninja_profile.set_preference("dom.webdriver.enabled", False)
        ninja_profile.set_preference("useAutomationExtension", False)
        ninja_profile.update_preferences()
        options.profile = ninja_profile
        if ip:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Firefox(options=options)

    def create_headless_firefox(self, profile, options, ip):
        """
        Creates a headless Firefox browser instance.
        """
        if not options:
            options = webdriver.FirefoxOptions()
        options.headless = True
        return self.create_firefox(profile, options, ip)

    def create_ie(self, profile, options, ip):
        """
        Creates an Internet Explorer browser instance. Note: IE is deprecated in Selenium 4.
        """
        if profile is not None:
            self.log.warning('IE was instantiated with a profile which is a Firefox exclusive parameter.')
        if not options:
            options = webdriver.IeOptions()
        if ip:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Ie(options=options)

    def create_edge(self, profile, options, ip):
        """
        Creates a Microsoft Edge browser instance.
        """
        if profile is not None:
            self.log.warning('Edge was instantiated with a profile which is not applicable.')
        if not options:
            options = webdriver.EdgeOptions()
        if ip:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Edge(options=options)

    def create_safari(self, profile, options, ip):
        """
        Creates a Safari browser instance.
        """
        if not options:
            options = SafariOptions()
        if ip:
            options.add_argument(f'--proxy-server={ip}')
        return webdriver.Safari(options=options)