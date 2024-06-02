import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from ..logger import Logger
from ._driver import Driver


class Base(Driver):

    def __init__(self, root):
        """
        Base class with the browser driver and fundamental functions
        :param root: the main Browser class
        """
        super().__init__(root)
        self.log = Logger.get_logger()
        self._strategies = {
            'id': self._find_by_id,
            'name': self._find_by_name,
            'xpath': self._find_by_xpath,
            'link': self._find_by_link_text,
            'partial link': self._find_by_partial_link_text,
            'css': self._find_by_css_selector,
            'class': self._find_by_class_name,
            'tag': self._find_by_tag_name,
        }
        self._strategy_alias = {
            # by identifier
            'identifier': 'identifier',
            # by id
            'id': 'id', 'by id': 'id', 'by_id': 'id', '#': 'id',
            # by name
            'name': 'name', 'by name': 'name', 'by_name': 'name',
            # by xpatch
            'xpath': 'xpath', 'x': 'xpath', 'x path': 'xpath', 'path': 'xpath',
            # by dom
            'dom': 'dom',
            # by link
            'link': 'link', '@': 'link', 'link text': 'link',
            # by partial link
            'partial': 'partial link', 'partial link': 'partial link',
            'plink': 'partial link', 'partial_link': 'partial link',
            # by css
            'css': 'css', 'css path': 'css', 'css_path': 'css',
            # by class name
            'class name': 'class', 'class': 'class', 'class_name': 'class',
            # by tag
            'tag': 'tag',
        }

    def find_element(self, locator, required=True, parent=None, first_only=True) -> WebElement:
        """ Main method used to find elements. Will call the right method
        based on the locator provided

        - The ``locator`` can be specified to use an explicit strategy, such as
          find_element_by_xpath('//path') in selenium is equivalent to
          find_element('xpath://path'). Available strategies are:
          'identifier', 'id', 'name', 'xpath', 'dom', 'link', 'patial link',
          'css', 'class name', 'jquery' and 'tag'

        - Some locator strategies have shortcuts. Such as `locators` starting
          with '#' will find elements with IDs. exp: #myId will look for
          elements with an ID of 'myId'
          Shortcuts:
            # 1- A valid xpath as a locator will automatically use the xPath
                 strategy
            # 2- A string starting with `#` will look for IDs with the id
                 following the `#` symbol.
                 find_element('#myId') === find_element('id:myId')
            # 3- A string starting with `@` will look for links with the text
                 following the `@` symbol.
                 find_element('@login') === find_element('link:login')

        - By default, ``required`` is set to True which will throw a
          NoSuchElementException if the element is not found. Set ``required``
          to False to return None if the element is not found.

        - Provide a ``parent`` WebElement to narrow the search to the sub nodes
          of the parent node. NOTE: if xPath is used, xPath may still return
          ALL nodes that match, and not just the sub nodes. Make sure to
          prepend '.' to limit the search to the parent's sub nodes.

        - ``first_only`` will limit the search result to the first matching
          element. In find_elements, we set ``first_only`` to False return a
          list of elements.

        :param locator: str
        :param required: bool - [required] will raise 'ElementNotFound' exception
            if element isn't found. [not required] will return 'None'
        :param parent: WebElement - the driver or parent element
        :param first_only: bool - return all elements or only the first
        :return WebElement:
        """
        if parent and not self._is_webelement(parent):
            raise ValueError(f'Parent must be Selenium WebElement but it '
                             f'was {type(parent)}.')
        if self._is_webelement(locator):
            return locator
        strategy, query = self._get_strategy(locator)
        strategy_method = self._strategies[self._strategy_alias[strategy]]
        elements = strategy_method(query, parent=parent or self.driver)
        if required and not elements:
            msg = f'Element with locator "{locator}" not found. it was' \
                  f' parsed as strategy="{strategy}" and query="{query}"'
            raise NoSuchElementException(msg)
        if first_only:
            if not elements:
                self.log.info(f'Element with locator "{locator}" not '
                              f'found. It was parsed as strategy="{strategy}" '
                              f'and query="{query}"')
                return None
            return elements[0]
        return elements

    def find_elements(self, locator, required=False, parent=None):
        """
        Function will return a list of matching WebElements instead of a
        single WebElement as `find_element` does.

        See `find_element` for ``locator`` usage and function details.

        :param locator: str
        :param required: bool - [required] will raise 'ElementNotFound' exception
            if element isn't found. [not required] will return 'None'
        :param parent: WebElement - the driver or parent element
        :return: List[WebElement]
        """
        return self.find_element(locator, required, parent, False)

    def is_text_present(self, text):
        """
        See if page to contains `text`. This will not look into the page source
        for text, but will use xpath to find a node that contains the text.
        Use get_source() to find text in the page's source.

        :param text: str
        :return: bool
        """
        locator = "xpath://*[contains(., %s)]" % self._escape_xpath_value(text)
        return self.find_element(locator, required=False) is not None

    def is_enabled(self, locator):
        """
        See if an element located by ``locator`` is enabled.

        See `find_element()` for ``locator`` syntax.

        :param locator: str or WebElement
        :return:
        """
        element = self.find_element(locator, required=False)
        if element is None:
            return None
        return (element.is_enabled() and
                element.get_attribute('readonly') is None)

    def is_visible(self, locator):
        """
        See if an element located by ``locator`` is visible.
        Visibility is determined by selenium and looks for attributes /
        properties such as <input> with type 'hidden', NOSCRIPT elements
        `dom.isElement(elem, goog.dom.TagName.NOSCRIPT)`, styles set as
        'visibility':'hidden' or 'display':'none', opacity set to zero, etc.
        Selenium will also look for the element's parent's visibility to
        determine this element's visibility.

        See `find_element()` for ``locator`` syntax.

        :param locator: str or WebElement
        :return:
        """
        element = self.find_element(locator, required=False)
        return element.is_displayed() if element else None

    def _get_strategy(self, locator):
        """support method used to parse the locator into two string
        'id:element'            returns     'id' and 'element'
        'class name = myClass'  returns     'class name' and 'myClass'
        """
        if locator.startswith(('/', '(', '.')):
            return 'xpath', locator
        if locator.startswith('#'):
            return 'id', locator[1:]
        if locator.startswith('@'):
            return 'link', locator[1:]
        groups = re.search('^((\w+ )?(\w+)) ?[:=] ?(.+)', locator)
        # parse locator into "strategy" and "element"
        # 'class name = spicy' returns 'class name' and 'spicy'
        if groups is None:
            raise ValueError(
                f'Was not able to parse locator "{locator}". Example usage '
                f'"id:theID"')
        strategy = groups.group(1)
        element = groups.group(4)
        return strategy.lower(), element

    def _is_webelement(self, element):
        return isinstance(element, WebElement)

    def _find_by_id(self, query, parent):
        return parent.find_elements(By.ID, query)

    def _find_by_name(self, query, parent):
        return parent.find_elements(By.NAME, query)

    def _find_by_xpath(self, query, parent):
        return parent.find_elements(By.XPATH, query)

    def _find_by_link_text(self, query, parent):
        return parent.find_elements(By.LINK_TEXT, query)

    def _find_by_partial_link_text(self, query, parent):
        return parent.find_elements(By.PARTIAL_LINK_TEXT, query)

    def _find_by_css_selector(self, query, parent):
        return parent.find_elements(By.CSS_SELECTOR, query)

    def _find_by_class_name(self, query, parent):
        return parent.find_elements(By.CLASS_NAME, query)

    def _find_by_tag_name(self, query, parent):
        return parent.find_elements(By.TAG_NAME, query)

    def _escape_xpath_value(self, value):
        # https://stackoverflow.com/questions/14822153/escape-single-quote-in-xpath-with-nokogiri
        # if you wanted to match the string: "That's mine", he said.,
        # you would need to do something like:
        #   text()=concat('"That', "'", 's mine", he said.')
        if '"' in value and '\'' in value:
            parts_wo_apos = value.split('\'')
            return f"concat('%s')" % "', \"'\", '".join(parts_wo_apos)
        if '\'' in value:
            return f"\"{value}\""
        return f"'{value}'"
