from collections import namedtuple
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


from ..config import *
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
        self.log.info(f'Cleared text at {locator}.')
        self.find_element(locator).clear()

    def click_button(self, locator):
        """
        Click button identified by locator. Will automatically append
        the correct tag to help pinpoint the button

        See `find_element` method in `_base.py` for ``locator`` usage/syntax

        :param locator: WebEelement or str
        :return: NoReturn
        """
        self.log.info(f'Clicking button {locator}.')
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
        self.log.info(f'Clicking element {locator}.')
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
        self.log.info(f'Clicking element {locator} at coordinates x={xoffset}, '
                      f'y={yoffset}')
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
        self.log.info(f'Clicking image {locator}.')
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
        self.log.info(f'Double clicking element {locator}')
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
        self.log.info(f'Dragging {locator} onto {target}')
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
        self.log.info(f'Dragging {locator} {xoffset} px on the x axis and '
                      f'{yoffset} px on the y axis')
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
        return False  # element not found

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

    def right_click_element_at_coordinates(self, locator, xoffset, yoffset):
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
        action.context_click()
        action.perform()

    def send_keys(self, locator=None, *keys):
        """
        Send keys to element or page. Use `None` as locator to send keys to page
        Can chain keys by providing separate function arguments

        Example:
        _.send_keys('#myElem', 'my word')         sends 'my word'
        _.send_keys(None, 'F12')                  sends 'F12' to browser
        _.send_keys('#myElem', 'my', ' ', 'word') sends 'my word'
        _.send_keys('#myElem', 'CTRL', 'a')       holds 'CTRL', send a, release 'CTRL'

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
            self.log.info(f'Sending key(s) {keys} to {locator} element.')
        else:
            self.log.info(f'Sending key(s) {str(keys)} to page.')
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
        self.log.info(f'Simulating Mouse Down on element {locator}.')
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
        self.log.info(f'Simulating Mouse Out on element {locator}.')
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
        self.log.info(f'Simulating Mouse Over on element {locator}.')
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
        self.log.info(f'Simulating Mouse Up on element {locator}.')
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
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

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

    def _press_keys(self, locator, parsed_keys):
        element = None
        if locator is not None:
            element = self.find_element(locator)

        actions = ActionChains(self.driver)
        keys_down = []
        for key in parsed_keys:
            if key.key_code is None:
                self._press_normal_keys(actions, element, key.original)
            else:
                if len(parsed_keys) == 1:
                    # only one special key = not a modifier, but a special key
                    # to send to element or browser.
                    self._press_normal_keys(actions, element, key.key_code)
                else:
                    # complex chain of actions - speciel key acts as a modifier
                    self._press_special_keys(actions, key)
                    keys_down.append(key)
        for key_down in keys_down:
            self.log.info(f'Releasing special key {key_down.original}.')
            actions.key_up(key_down.key_code)
        actions.perform()

    def _parse_keys(self, *keys):
        if not keys:
            raise AssertionError('"keys" argument can not be empty.')
        list_keys = []
        for key in keys:
            Key = namedtuple('Key', 'original, key_code')
            parsed_key = self._parse_alias(key)
            if hasattr(Keys, self._parse_alias(key)):
                list_keys.append(Key(key, getattr(Keys, parsed_key)))
            else:
                list_keys.append(Key(key, None))
        return list_keys

    def _parse_alias(self, key):
        tmp = key.upper()
        if tmp in ['CONTROL', 'CNTRL', 'CTRL']:
            return 'CONTROL'
        if tmp in ['SHIFT', 'SHFT', 'LSHFT', 'UPPER']:
            return 'SHIFT'
        if tmp in ['ESCAPE', 'ESC', 'ECS', 'EXIT']:
            return 'ESCAPE'
        return key

    def _press_normal_keys(self, actions, element, key):
        self.log.info(f'Sending key(s) {key}')
        if element:
            actions.send_keys_to_element(element, key)
        else:
            actions.send_keys(key)

    def _press_special_keys(self, actions, key):
        self.log.info(f'Pressing special key {key.original} down.')
        actions.key_down(key.key_code)
