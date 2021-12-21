from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from ..config import *
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
        self.log = Logger().log

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
            # ninja chrome - anti robot detection browser in chrome
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

            # TODO: add other browsers
            # 'opera' : 'opera',
            # 'safari' : 'safari',
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

    def create_driver(self, browser, desired_capabilities=None, profile=None,
                      options=None, ip=None):
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

        return creation_method(desired_capabilities, profile, options, ip)

    def get_creation_method(self, browser):
        """
        Fetch browser specific creation method required by create_driver() method
        :param browser: A string representing the desired browser
        :return: driver creation method
        """
        return getattr(self, f'create_{self.browser_name(browser.lower())}')

    ############################################################################
    # browser specific creation methods

    def create_chrome(self, desired_capabilities, profile, options, ip):
        if profile is not None:
            self.log.warning('Chrome was instantiated with a profile which is a '
                             'firefox exclusive parameter.')
        if desired_capabilities is not None:
            default_desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            default_desired_capabilities.update(desired_capabilities)
            desired_capabilities = default_desired_capabilities
        else:
            desired_capabilities = {}
        if ip is not None:
            self.insert_ip(desired_capabilities, ip)
        return webdriver.Chrome(desired_capabilities=desired_capabilities,
                                options=options)

    def create_chrome_ninja(self, desired_capabilities, profile, options, ip):
        """
        Recommended to edit chromedriver.exe by replacing all 'cdc_' text to
        'dog_' or anything else. Also, `Options` argument is ignored.
        """
        if options is not None:
            self.log.warning('Chrome ninja received `options` which will be '
                             'ignored and replaced by `ninja options`.')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches",
                                        ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = self.create_chrome(desired_capabilities, profile, options, ip)
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

    def create_headless_chrome(self, desired_capabilities, profile, options, ip):
        if options is None:
            options = webdriver.ChromeOptions()
        options.headless = True
        return self.create_chrome(desired_capabilities, profile, options, ip)

    def create_firefox(self, desired_capabilities, profile, options, ip):
        if desired_capabilities is not None:
            default_desired_capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
            default_desired_capabilities.update(desired_capabilities)
            desired_capabilities = default_desired_capabilities
        else:
            desired_capabilities = {}
        if ip is not None:
            self.insert_ip(desired_capabilities, ip)
        return webdriver.Firefox(desired_capabilities=desired_capabilities,
                                 firefox_profile=profile, options=options)

    def create_firefox_ninja(self, desired_capabilities, profile, options, ip):
        """
        Recommended to edit chromedriver.exe by replacing all 'cdc_' text to
        'dog_' or anything else. Also, `profile` argument is ignored.
        """
        if profile is not None:
            self.log.warning('Firefox ninja received a `profile` which will be '
                             'ignored and replaced by `ninja profile`.')
        profile = FirefoxProfile()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        if desired_capabilities is None:
            desired_capabilities = DesiredCapabilities.FIREFOX
        desired_capabilities['marionette'] = True

        return self.create_firefox(desired_capabilities, profile, options, ip)

    def create_headless_firefox(self, desired_capabilities, profile, options, ip):
        if options is None:
            options = webdriver.FirefoxOptions()
        options.headless = True
        return self.create_firefox(desired_capabilities, profile, options, ip)

    def create_ie(self, desired_capabilities, profile, options, ip):
        if profile is not None:
            self.log.warning('IE was instantiated with a profile which is a firefox exclusive parameter.')
        if desired_capabilities is not None:
            default_desired_capabilities = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
            default_desired_capabilities.update(desired_capabilities)
            desired_capabilities = default_desired_capabilities
        else:
            desired_capabilities = {}
        if ip is not None:
            self.insert_ip(desired_capabilities, ip)
        return webdriver.Ie(desired_capabilities=desired_capabilities,
                            options=options)

    def create_edge(self, desired_capabilities, profile, options, ip):
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
        if ip is not None:
            self.insert_ip(desired_capabilities, ip)
        return webdriver.Edge(capabilities=desired_capabilities)

    def insert_ip(self, desired_capabilities, ip):
        desired_capabilities['proxy'] = {
            'proxyType': 'MANUAL',
            'sslProxy': ip,
            'httpProxy': ip,
        }
        return desired_capabilities
