from ..config import *

# external
from collections import namedtuple
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# internal
from ..logger import Logger
from ._base import Base


class Element(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def clear_element_text(self, locator):
		"""
		Clears the value of text entry element identified by locator.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebEelement or str
		:return: NoReturn
		"""
		self.log.info('Cleared text at {}.'.format(locator))
		self.find_element(locator).clear()

	def click_button(self, locator):
		"""
		Click button identified by locator. Will automatically append
		the correct tag to help pinpoint the button

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebEelement or str
		:return: NoReturn
		"""
		self.log.info('Clicking button {}.'.format(locator))
		element = self.find_element(locator, tag='input', required=False)
		if not element:
			element = self.find_element(locator, tag='button')
		element.click()

	def click_element(self, locator):
		"""
		Click element identified by locator. Will automatically append
		the correct tag to help pinpoint the element.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebEelement or str
		:return: NoReturn
		"""
		self.log.info('Clicking element {}.'.format(locator))
		self.find_element(locator).click()

	def click_element_at_coordinates(self, locator, xoffset, yoffset):
		"""
		Cursor is moved at the center of the element and x/y coordinates are
		calculated from that point.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebEelement or str
		:param xoffset: X offset to move to, as a positive or negative integer.
		:param yoffset: Y offset to move to, as a positive or negative integer.
		:return:
		"""
		self.log.info('Clicking element {} at coordinates x={}, y={}'.format(
			locator, xoffset, yoffset
		))
		element = self.find_element(locator)
		action = ActionChains(self.driver)
		action.move_to_element(element)
		action.move_by_offset(xoffset, yoffset)
		action.click()
		action.perform()

	def click_image(self, locator):
		"""
		Click image identified by locator. Will automatically append
		the correct tag to help pinpoint the image

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Clicking image {}.'.format(locator))
		element = self.find_element(locator, tag='image', required=False)
		if not element:
			# A form may have an image as it's submit trigger.
			element = self.find_element(locator, tag='input')
		element.click()

	def double_click_element(self, locator):
		"""
		Double click element identified by the locator

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Double clicking element {}'.format(locator))
		element = self.find_element(locator)
		action = ActionChains(self.driver)
		action.double_click(element).perform()

	def drag_and_drop(self, locator, target):
		"""
		Drags element identified by ``locator`` into ``target`` element.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		Example:
			ff.drag_and_drop('css:div#element','css:div.target')
		:param locator: WebElement or str
		:param target: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Dragging {} onto {}'.format(locator, target))
		element = self.find_element(locator)
		target = self.find_element(target)
		action = ActionChains(self.driver)
		action.drag_and_drop(element, target).perform()

	def drag_and_drop_by_offset(self, locator, xoffset, yoffset):
		"""
		Drags element identified with ``locator`` by ``xoffset/yoffset``.
		Example:
			ff.drag_and_drop_by_offset(myElem, 50, -35) #50px right, 35px down

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param xoffset: X offset to move to, as a positive or negative integer.
		:param yoffset: Y offset to move to, as a positive or negative integer.
		:return: NoReturn
		"""
		self.log.info('Dragging {} {} px on the x axis and {} px '
		              'on the y axis'.format(locator, xoffset, yoffset))
		element = self.find_element(locator)
		action = ActionChains(self.driver)
		action.drag_and_drop_by_offset(element, int(xoffset), int(yoffset))
		action.perform()

	def element_text_contains(self, locator, expected, ignore_case=True):
		"""
		See if an expected text exists in an element.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param expected: str - the text that needs to be found
		:param ignore_case: bool - set to false to make the comparison case
			sensitive
		:return: bool - confirms that text exists or not in the element
		"""
		element = self.find_element(locator, required=False)
		if element is not None:
			text = element.text.lower() if ignore_case else element.text
			expected = expected.lower() if ignore_case else expected
			return expected in text
		return False # element not found

	def element_text_is(self, locator, expected, ignore_case=False):
		"""
		See if an expected text is equal to the element's text.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator:
		:param expected:
		:param ignore_case:
		:return:
		"""
		element = self.find_element(locator, required=False)
		if element is not None:
			text = element.text.lower() if ignore_case else element.text
			expected = expected.lower() if ignore_case else expected
			return text == expected
		return False  # element not found

	def get_element_attribute(self, locator, attribute):
		"""
		Get an element's attribute such as:
		<input type="text" value="Name:"> if ``attribute`` is 'value'
		returns "Name:"

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param attribute: str
		:return: str
		"""
		return self.find_element(locator).get_attribute(attribute)

	def get_element_property(self, locator, prop):
		"""
		Get an element's property such as:
		<input type="text" value="Name:"> if property is value
		returns current value, not the initial state; so "John" for exp

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param prop: str
		:return: str
		"""
		return self.find_element(locator).get_property(prop)

	def get_element_size(self, locator):
		"""
		returns the width and height of the element as integers

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: int, int
		"""
		element = self.find_element(locator)
		return element.size['width'], element.size['height']

	def get_text(self, locator):
		"""
		return the text of an element

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: str
		"""
		return self.find_element(locator).text

	def page_contains_text(self, text):
		"""
		Checks entire page and all frames for specific text
		This is not the same as looking into the page's source

		:param text: str - text we want to assert is present
		:return: bool
		"""
		self.driver.switch_to.default_content()
		if self.is_text_present(text):
			return True

		frames = self.find_elements('xpath://frame|//iframe')
		for frame in frames:
			self.driver.switch_to.frame(frame)
			if self.is_text_present(text):
				self.driver.switch_to.frame(frame)
				found_text = self.is_text_present(text)
				self.driver.switch_to.default_content()
				if found_text:
					return True
			return False

	def send_keys(self, locator=None, *keys):
		"""
		Send keys to element or page. Use `None` as locator to send keys to page
		Can chain keys with `+` or provide as separate function arguments

		Example:
		_.send_keys('#myElem', 'my word')         sends 'my word'
		_.send_keys(None, 'F12')                  sends 'F12' to browser
		_.send_keys('#myElem', 'w+o+r+d')         sends 'word'
		_.send_keys('#myElem', 'my', ' ', 'word') sends 'my word'
		_.send_keys('#myElem', 'my+ +word')       same as above
		_.send_keys('#myElem', 'CTRL+a')          holds 'CTRL', send a, release 'CTRL'
		_.send_keys('#myElem', 'CTRL', 'a')       same as above

		`` special keys ``
		ADD, ALT, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT, ARROW_UP, BACKSPACE
		BACK_SPACE, CANCEL, CLEAR, COMMAND, CTRL, DECIMAL, DELETE
		DIVIDE, DOWN, END, ENTER, EQUALS, ESC, F1, F10, F11, F12, F2
		F3, F4, F5, F6, F7, F8, F9, HELP, HOME, INSERT, LEFT, LEFT_ALT
		LEFT_CONTROL, LEFT_SHIFT, META, MULTIPLY, NULL, NUMPAD0, NUMPAD1
		NUMPAD2, NUMPAD3, NUMPAD4, NUMPAD5, NUMPAD6, NUMPAD7, NUMPAD8
		NUMPAD9, PAGE_DOWN, PAGE_UP, PAUSE, RETURN, RIGHT, SEMICOLON
		SEPARATOR, SHIFT, SPACE, SUBTRACT, TAB, UP

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: str, WebElement or None
		:param keys: str or List[str]
		:return: NoReturn
		"""
		parsed_keys = self._parse_keys(*keys)
		if locator is not None:
			self.log.info('Sending key(s) {} to {} element.'.format(keys, locator))
		else:
			self.log.info('Sending key(s) {} to page.'.format(str(keys)))
		self._press_keys(locator, parsed_keys)

	def highlight_elements(self, locator, tag=None):
		"""
		Will cover elements identified by locator with a blue div without
		breaking page

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param tag: str
		:return: NoReturn
		"""
		elements = self.find_elements(locator, tag=tag)
		if not elements:
			self.log.info('Attempted to highlight elements, but none were found.')
			return
		self.log.info('Highlighting {} element(s)'.format(len(elements)))
		for element in elements:
			script = """
				old_element = arguments[0];
				let newDiv = document.createElement('div');
				newDiv.setAttribute("name", "covered");
				newDiv.style.backgroundColor = 'blue';
				newDiv.style.zIndex = '999';
				newDiv.style.top = old_element.offsetTop + 'px';
				newDiv.style.left = old_element.offsetLeft + 'px';
				newDiv.style.height = old_element.offsetHeight + 'px';
				newDiv.style.width = old_element.offsetWidth + 'px';
				old_element.parentNode.insertBefore(newDiv, old_element);
				old_element.remove();
				newDiv.parentNode.style.overflow = 'hidden';
	        """
			self.driver.execute_script(script, element)

	def mouse_down(self, locator):
		"""
		Simulates pressing the left mouse button on the element ``locator``.
		The element is pressed without releasing the mouse button.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Simulating Mouse Down on element {}.'.format(locator))
		element = self.find_element(locator)
		action = ActionChains(self.driver)
		action.click_and_hold(element).perform()

	def mouse_out(self, locator):
		"""
		Simulates moving mouse away from the element ``locator``.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Simulating Mouse Out on element {}.'.format(locator))
		element = self.find_element(locator)
		size = element.size
		offsetx = (size['width'] / 2) + 1
		offsety = (size['height'] / 2) + 1
		action = ActionChains(self.driver)
		action.move_to_element(element).move_by_offset(offsetx, offsety)
		action.perform()

	def mouse_over(self, locator):
		"""
		Simulates hovering mouse over the element ``locator``.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Simulating Mouse Over on element {}.'.format(locator))
		element = self.find_element(locator)
		action = ActionChains(self.driver)
		action.move_to_element(element).perform()

	def mouse_up(self, locator):
		"""
		Simulates releasing the left mouse button on the element ``locator``.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info('Simulating Mouse Up on element {}.'.format(locator))
		element = self.find_element(locator)
		ActionChains(self.driver).release(element).perform()

	def set_focus_to_element(self, locator):
		"""
		Sets focus to element identified by the locator.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		element = self.find_element(locator)
		self.driver.execute_script("arguments[0].focus();", element)

	def scroll_element_into_view(self, locator):
		"""
		Scrolls an element identified by ``locator`` into view.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		element = self.find_element(locator)
		ActionChains(self.driver).move_to_element(element).perform()

	def simulate_event(self, locator, event):
		"""
		Simulates ``event`` on element identified by ``locator``.
		example of accepted events are 'onerror', 'onload', 'onclick' ...

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param event: str
		:return: NoReturn
		"""
		element = self.find_element(locator)
		script = """
			element = arguments[0];
			eventName = arguments[1];
			if (document.createEventObject) { // IE
			    return element.fireEvent(eventName, document.createEventObject());
			}
			var evt = document.createEvent("HTMLEvents");
			evt.initEvent(eventName, true, true);
			return !element.dispatchEvent(evt);
	        """
		self.driver.execute_script(script, element, event)

	######################################################
	### Snippets below from Robot Framework Foundation ###
	######################################################
	def _convert_special_keys(self, keys):
		KeysRecord = namedtuple('KeysRecord', 'converted, original')
		converted_keys = []
		for key in keys:
			key = self._parse_aliases(key)
			if self._selenium_keys_has_attr(key):
				converted_keys.append(KeysRecord(getattr(Keys, key), key))
			else:
				converted_keys.append(KeysRecord(key, key))
		return converted_keys

	def _press_keys(self, locator, parsed_keys):
		if locator is not None:
			element = self.find_element(locator)
		else:
			element = None
		for parsed_key in parsed_keys:
			actions = ActionChains(self.driver)
			special_keys = []
			for key in parsed_key:
				if self._selenium_keys_has_attr(key.original):
					special_keys = self._press_keys_special_keys(actions,
					                                             element,
					                                             parsed_key,
					                                             key,
					                                             special_keys)
				else:
					self._press_keys_normal_keys(actions, element, key)
			for special_key in special_keys:
				self.log.info('Releasing special key %s.' % special_key.original)
				actions.key_up(special_key.converted)
			actions.perform()

	def _parse_aliases(self, key):
		if key == 'CTRL':
			return 'CONTROL'
		if key == 'ESC':
			return 'ESCAPE'
		return key

	def _parse_keys(self, *keys):
		if not keys:
			raise AssertionError('"keys" argument can not be empty.')
		list_keys = []
		for key in keys:
			separate_keys = self._separate_key(key)
			separate_keys = self._convert_special_keys(separate_keys)
			list_keys.append(separate_keys)
		return list_keys

	def _press_keys_normal_keys(self, actions, element, key):
		self.log.info('Sending key(s) %s' % key.converted)
		if element:
			actions.send_keys_to_element(element, key.converted)
		else:
			actions.send_keys(key.converted)

	def _press_keys_special_keys(self, actions, element, parsed_key, key,
	                             special_keys):
		if len(parsed_key) == 1 and element:
			self.log.info('Pressing special key %s to element.' % key.original)
			actions.send_keys_to_element(element, key.converted)
		elif len(parsed_key) == 1 and not element:
			self.log.info('Pressing special key %s to browser.' % key.original)
			actions.send_keys(key.converted)
		else:
			self.log.info('Pressing special key %s down.' % key.original)
			actions.key_down(key.converted)
			special_keys.append(key)
		return special_keys

	def _selenium_keys_has_attr(self, key):
		try:
			return hasattr(Keys, key)
		except UnicodeError:  # To support Python 2 and non ascii characters.
			return False

	def _separate_key(self, key):
		one_key = ''
		list_keys = []
		for char in key:
			if char == '+' and one_key != '':
				list_keys.append(one_key)
				one_key = ''
			else:
				one_key += char
		if one_key:
			list_keys.append(one_key)
		return list_keys

	######################################################
	### END of snippet from Robot Framework Foundation ###
	######################################################