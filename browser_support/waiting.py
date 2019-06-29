from ..config import *

# external
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


# internal
from ..logger import Logger
from ._base import Base


class Waiting(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log


	def wait_for_element(self, locator, negate=False, timeout=DEFAULT_TIMEOUT):
		"""
		Wait for `element` and return it if found or raise timeoutException

		Set ``negate`` to True to exit explicit wait when the element is no
		longer present

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - explicit wait timeout in seconds
		:return: WebElement or TimeoutException
		"""
		func = lambda _: self.find_element(locator, required=False)
		if negate:
			self.log.info(
				'Waiting for element `{}` to not be present.'.format(locator))
			message = ('Failed to wait for element `{}` to be removed before '
			           'the timeout [{} seconds].'.format(locator, timeout))
			return self._wait_until_not(func, timeout, message)
		else:
			self.log.info(
				'Waiting for element `{}` to be present.'.format(locator))
			message = ('Failed to wait for element `{}` before the '
			           'timeout [{} second(s)].'.format(locator, timeout))
			return self._wait_until(func, timeout, message)

	def wait_for_element_to_be_enabled(self, locator, negate=False,
	                                   timeout=DEFAULT_TIMEOUT):
		"""
		Wait for `element` to be to enabled or raise timeoutException.

		Set ``negate`` to True to exit explicit wait when the element is disabled
		Returns bool result.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - explicit wait timeout in seconds
		:return: bool or TimeoutException
		"""
		func = lambda _: self.is_element_enabled(locator)
		if negate:
			self.log.info(
				'Waiting for element `{}` to be disabled.'.format(locator))
			message = ('Failed to wait for element `{}` to be disabled before '
			           'the timeout [{} second(s)].'.format(locator, timeout))
			return self._wait_until_not(func, timeout, message)
		else:
			self.log.info(
				'Waiting for element `{}` to be enabled.'.format(locator))
			message = ('Failed to wait for element `{}` to be enabled before '
			           'the timeout [{} second(s)].'.format(locator, timeout))
			return self._wait_until(func, timeout, message)

	def wait_for_element_to_be_visible(self, locator, negate=False,
	                                   timeout=DEFAULT_TIMEOUT):
		"""
		Wait for `element` to be to visible or raise timeoutException.
		An invisible element is determined by selenium and looks for attributes /
		properties such as <input> with type 'hidden', NOSCRIPT elements
		`dom.isElement(elem, goog.dom.TagName.NOSCRIPT)`, styles set as
		'visibility':'hidden' or 'display':'none', opacity set to zero, etc.
		Selenium will also look for the element's parent's visibility to
		determine this element's visibility.

		Set ``negate`` to True to exit explicit wait when the element is invisible
		Returns bool result.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - explicit wait timeout in seconds
		:return: bool or TimeoutException
		"""
		func = lambda _: self.is_visible(locator)
		if negate:
			self.log.info(
				'Waiting for element `{}` to be invisible.'.format(locator))
			message = ('Failed to wait for element `{}` to be invisible before'
			           ' the timeout [{} seconds].'.format(locator, timeout))
			return self._wait_until_not(func, timeout, message)
		else:
			self.log.info(
				'Waiting for element `{}` to be visible.'.format(locator))
			message = ('Failed to wait for element `{}` to be visible before'
			           ' the timeout [{} seconds].'.format(locator, timeout))
			return self._wait_until(func, timeout, message)

	def wait_for_element_to_contain(self, locator, text, negate=False,
	                                timeout=DEFAULT_TIMEOUT):
		"""
		Wait for `element` to contain `text`.

		Set ``negate`` to True to wait for `element` to NOT contain `text`.
		Returns bool result.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param text: str - text searched
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - explicit wait timeout in seconds
		:return: bool or TimeoutException
		"""
		func = lambda _: text in self.find_element(locator).text
		if negate:
			self.log.info(
				'Waiting for element `{}` to not contain {}.'.format(locator, text))
			message = ('Failed to wait for element `{}` to not contain `{}` before'
			           ' the timeout [{} seconds].'.format(locator, text, timeout))
			return self._wait_until_not(func, timeout, message)
		else:
			self.log.info(
				'Waiting for element `{}` to contain {}.'.format(locator, text))
			message = ('Failed to wait for element `{}` to contain `{}` before'
			           ' the timeout [{} seconds].'.format(locator, text, timeout))
			return self._wait_until(func, timeout, message)

	def wait_for_script(self, script, negate=False, timeout=DEFAULT_TIMEOUT,
	                    message='Condition `{}` not met before the timeout.'):
		"""
		Wait for `script` to be truthy and return the script's results or
		throws a TimeoutException.

		The script can be a JavaScript script, but must return a value to
		be evaluated.

		Set ``negate`` to True to exit explicit wait when the script returns falsy
		Returns the return of the javascript `script`

		Usage:
        wait_for_script( 'return document.title == "New Title"' )
        wait_for_script( 'return jQuery.active == 0' )
        wait_for_script( 'style = document.querySelector("h1").style; return style.background == "red" && style.color == "white"' )

		:param script: str - script that returns a value to evaluate
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - wait for up to `timeout` seconds
		:param message: str - custom error message in case of timeout
		:return: Any - the return of the provided script
		"""
		if 'return' not in script:
			raise ValueError('Condition `{}` did not have a mandatory `return`.'
			                 .format(script))
		func = lambda driver: driver.execute_script(script)
		message = message.format(script)
		self.log.info(
			'Waiting for script `{}` to return.'.format(script))
		if negate:
			return self._wait_until_not(func, timeout, message)
		else:
			return self._wait_until(func, timeout, message)

	def wait_for_page_to_contain(self, text, negate=False, timeout=DEFAULT_TIMEOUT):
		"""
		Wait for page to contain `text`. This will not look into the page source
		for text, but will use xpath to find a node that contains the text.
		Use get_source() to find text in the page's source.

		Set ``negate`` to True to wait for `element` to NOT contain `text`.
		Returns bool result.

		:param text: str - the text searched on the page
		:param negate: bool - True will wait for condition to be truthy, False
			will wait for the condition to be falsy
		:param timeout: int - wait for up to `timeout` seconds
		:return: bool or TimeoutException
		"""
		func = lambda _: self.is_text_present(text)
		if negate:
			self.log.info('Waiting for page to not contain `{}`.'.format(text))
			message = ('Failed to wait for page to not contain `{}` before the '
			           'timeout [{} seconds].'.format(text, timeout))
			return self._wait_until_not(func, timeout, message)
		else:
			self.log.info('Waiting for page to contain `{}`.'.format(text))
			message = ('Failed to wait for page to contain `{}` before the '
			           'timeout [{} seconds].'.format(text, timeout))
			return self._wait_until(func, timeout, message)

	def _wait_until(self, func, timeout, message):
		try:
			result = WebDriverWait(self.driver, timeout=timeout).until(func)
			return result
		except TimeoutException as excp:
			excp.msg = message
			raise

	def _wait_until_not(self, func, timeout, message):
		try:
			result = WebDriverWait(self.driver, timeout=timeout).until_not(func)
			return result
		except TimeoutException as excp:
			excp.msg = message
			raise
