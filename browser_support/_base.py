from ..config import *

# external
import re
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

# internal
from ..logger import Logger
from ._driver import Driver


class Base(Driver):

	def __init__(self, root):
		"""
		Base class with the browser driver and fundamental functions
		:param root: the main Browser class
		"""
		super().__init__(root)
		self.log = Logger().log
		self._strategies = {
			'identifier': self._find_by_identifier,
			'id': self._find_by_id,
			'name': self._find_by_name,
			'xpath': self._find_by_xpath,
			'dom': self._find_by_dom,
			'link': self._find_by_link_text,
			'partial link': self._find_by_partial_link_text,
			'css': self._find_by_css_selector,
			'class': self._find_by_class_name,
			'jquery': self._find_by_jquery_selector,
			'tag': self._find_by_tag_name,
			'default': self._find_by_default
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
			'css': 'css', 'css path': 'css', 'css_path':'css',
			# by class name
			'class name': 'class', 'class': 'class', 'class_name': 'class',
			# by jQuery
			'jquery':'jquery', 'jq': 'jquery', 'j query': 'jquery',
			# by tag
			'tag': 'tag',
			# by default
			'default': 'default',
		}

	def find_element(self, locator, tag=None, required=True, parent=None,
	                 first_only=True) -> WebElement:
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
			     find_element('@loging') === find_element('link:login')

        - If a ``tag`` is included, it will filter the result of the search
          as an additional constraint.

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

		:param locator: str or WebElement
		:param tag: str - tags used to filter the results, such as refine to
			"H1" elements only
		:param required: bool - [required] will raise 'ElementNotFound' exception
			if element isn't found. [not required] will return 'None'
		:param parent: WebElement - the driver or parent element
		:param first_only: bool - return all elements or only the first
		:return WebElement:
		"""
		element_type = 'Element' if not tag else tag.capitalize()
		if parent and not self._is_webelement(parent):
			raise ValueError('Parent must be Selenium WebElement but it '
			                 'was {}.'.format(type(parent)))
		if self._is_webelement(locator):
			return locator
		strategy, query = self._get_strategy(locator)
		strategy_method = self._strategies[self._strategy_alias[strategy]]
		tag, constraints = self._get_tag_and_constraints(tag)
		elements = strategy_method(query, tag, constraints,
		                    parent=parent or self.driver)
		if required and not elements:
			raise NoSuchElementException('{} with locator "{}" not found. '
			'it was parsed as strategy="{}" and query="{}"'.format(
				element_type, locator, strategy, query
			))
		if first_only:
			if not elements:
				self.log.info('{} with locator "{}" not found. '
					'it was parsed as strategy="{}" and query="{}"'.format(
						element_type, locator, strategy, query
					))
				return None
			return elements[0]
		return elements

	def find_elements(self, locator, tag=None, required=False, parent=None):
		"""
		Function will return a list of matching WebElements instead of a
		single WebElement as `find_element` does.

		See `find_element` for ``locator`` usage and function details.

		- Differences:
			# 1- Returns a list of matching WebElements
				 (even if only one is found)
			# 2- Can accept a list of Webelements to filter with the provided
				 ``tag``

		:param locator: List[WebElement] or str
			Can also use a list of webElements to refine with tags
		:param tag: str - tags used to filter the results, such as refine to
			"H1" elements only
		:param required: bool - [required] will raise 'ElementNotFound' exception
			if element isn't found. [not required] will return 'None'
		:param parent: WebElement - the driver or parent element
		:return: List[WebElement]
		"""
		if self._is_webelement(locator):
			return [locator] # find_elements must return a list
		if isinstance(locator, list):
			# if a list of web elements is provided, filter it using the provided tag
			for element in locator:
				if not self._is_webelement(element):
					raise ValueError(
						'"locator" must be a string or a list of WebElements '
						'but it was a list containing a {}.'.format(type(element)))
			tag, constraints = self._get_tag_and_constraints(tag)
			return self._filter(locator, tag, constraints)
		return self.find_element(locator, tag, required, parent, False)

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

	def is_enabled(self, locator, tag=None):
		"""
		See if an element located by ``locator`` is enabled.

		See `find_element()` for ``locator`` syntax.

		:param locator: str or WebElement
		:param tag: str
		:return:
		"""
		element = self.find_element(locator, tag, required=False)
		if element is None:
			return None
		return (element.is_enabled() and
		        element.get_attribute('readonly') is None)

	def is_visible(self, locator, tag=None):
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
		:param tag: str
		:return:
		"""
		element = self.find_element(locator, tag, required=False)
		return element.is_displayed() if element else None

	def _filter(self, elements, tag, constraints):
		"""Filter out elements that don't fit the tag and constraints"""
		if tag is None:
			return elements
		filtered_elements = []
		for element in elements: # filter individual elements
			if not element.tag_name.lower() == tag:
				continue # process next element if tags don't match
			if not constraints:
				filtered_elements.append(element)
				continue # no additional constrains and tags matched = append
			else: # tags match, but need to process the constrains
				for name in constraints:
					if isinstance(constraints[name], list):
						if element.get_attribute(name) in constraints[name]:
							filtered_elements.append(element)
							break # tag AND constrains matched = append
					elif element.get_attribute(name) == constraints[name]:
						filtered_elements.append(element)
						break # tag AND constrains matched = append
		return filtered_elements

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
				'Was not able to parse locator "{}". Example usage '
			'"id:theID"'.format(locator))
		strategy = groups.group(1)
		element = groups.group(4)
		return strategy.lower(), element

	def _get_tag_and_constraints(self, tag):
		if tag is None:
			return None, {}
		tag = tag.lower()
		constraints = {}
		if tag == 'link':
			tag = 'a'
		if tag == 'partial link':
			tag = 'a'
		elif tag == 'image':
			tag = 'img'
		elif tag == 'list':
			tag = 'select'
		elif tag == 'radio button':
			tag = 'input'
			constraints['type'] = 'radio'
		elif tag == 'checkbox':
			tag = 'input'
			constraints['type'] = 'checkbox'
		elif tag == 'text field':
			tag = 'input'
			constraints['type'] = ['date', 'datetime-local', 'email', 'month',
			                       'number', 'password', 'search', 'tel',
			                       'text', 'time', 'url', 'week', 'file']
		elif tag == 'file upload':
			tag = 'input'
			constraints['type'] = 'file'
		elif tag == 'text area':
			tag = 'textarea'
		return tag, constraints

	def _is_webelement(self, element):
		return isinstance(element, WebElement)

	def _find_by_identifier(self, query, tag, constraints, parent):
		# combines _find_by_id and _find_by_name
		elements = parent.find_elements_by_id(query) \
		           + parent.find_elements_by_name(query)
		return self._filter(elements, tag, constraints)

	def _find_by_id(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_id(query), tag, constraints)

	def _find_by_name(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_name(query),
		                    tag, constraints)

	def _find_by_xpath(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_xpath(query),
		                    tag, constraints)

	def _find_by_dom(self, query, tag, constraints, parent):
		if self._is_webelement(parent):
			raise ValueError('This method does not allow WebElement as parent')
		result = self.driver.execute_script("return {};".format(query))
		if result is None:
			return []
		if not isinstance(result, list):
			result = [result]
		return self._filter(result, tag, constraints)

	def _find_by_jquery_selector(self, query, tag, constraints, parent):
		if self._is_webelement(parent):
			raise ValueError('This method does not allow WebElement as parent')
		js = "return jQuery('{}').get();".format(query.replace("'", "\\'"))
		return self._filter(self.driver.execute_script(js),	tag, constraints)

	def _find_by_link_text(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_link_text(query),
			tag, constraints)

	def _find_by_partial_link_text(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_partial_link_text(query),
			tag, constraints)

	def _find_by_css_selector(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_css_selector(query),
			tag, constraints)

	def _find_by_class_name(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_class_name(query),
			tag, constraints)

	def _find_by_tag_name(self, query, tag, constraints, parent):
		return self._filter(parent.find_elements_by_tag_name(query),
			tag, constraints)

	######################################################
	### Snippets below from Robot Framework Foundation ###
	######################################################

	def _find_by_default(self, criteria, tag, constraints, parent):
		_key_attrs = {
			None: ['@id', '@name'],
			'a': ['@id', '@name', '@href',
			      'normalize-space(descendant-or-self::text())'],
			'img': ['@id', '@name', '@src', '@alt'],
			'input': ['@id', '@name', '@value', '@src'],
			'button': ['@id', '@name', '@value',
			           'normalize-space(descendant-or-self::text())']
		}
		if tag in _key_attrs:
			key_attrs = _key_attrs[tag]
		else:
			key_attrs = _key_attrs[None]
		xpath_criteria = self._escape_xpath_value(criteria)
		xpath_tag = tag if tag is not None else '*'
		xpath_constraints = self._get_xpath_constraints(constraints)
		xpath_searchers = ["%s=%s" % (attr, xpath_criteria) for attr in key_attrs]
		xpath_searchers.extend(self._get_attrs_with_url(key_attrs, criteria))
		xpath = "//%s[%s%s(%s)]" % (
			xpath_tag,
			' and '.join(xpath_constraints),
			' and ' if xpath_constraints else '',
			' or '.join(xpath_searchers)
		)
		return parent.find_elements_by_xpath(xpath)

	def _escape_xpath_value(self, value):
		if '"' in value and '\'' in value:
			parts_wo_apos = value.split('\'')
			return "concat('%s')" % "', \"'\", '".join(parts_wo_apos)
		if '\'' in value:
			return "\"%s\"" % value
		return "'%s'" % value

	def _get_attrs_with_url(self, key_attrs, criteria):
		attrs = []
		url = None
		xpath_url = None
		for attr in ['@src', '@href']:
			if attr in key_attrs:
				if url is None or xpath_url is None:
					url = self._get_base_url() + "/" + criteria
					xpath_url = self._escape_xpath_value(url)
				attrs.append("%s=%s" % (attr, xpath_url))
		return attrs

	def _get_base_url(self):
		url = self.driver.current_url
		if '/' in url:
			url = '/'.join(url.split('/')[:-1])
		return url

	def _get_xpath_constraints(self, constraints):
		xpath_constraints = [self._get_xpath_constraint(name, value)
		                     for name, value in constraints.items()]
		return xpath_constraints

	def _get_xpath_constraint(self, name, value):
		if isinstance(value, list):
			return "@%s[. = '%s']" % (name, "' or . = '".join(value))
		else:
			return "@%s='%s'" % (name, value)

	######################################################
	### END of snippet from Robot Framework Foundation ###
	######################################################