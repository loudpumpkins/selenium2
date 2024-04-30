from ..logger import Logger
from ._base import Base


class Frames(Base):

    def __init__(self, root):
        super().__init__(root)
        self.log = Logger.get_logger()

    def send_method_to_element_in_frame(self, frame_locator, element_locator, method):
        """
        Perform a Browser method on an element inside of a frame without having
        switch in and out of the frame.

        Can be used to send keys or get text to/from an element in a frame.
        The `frame_locator` can be a string such as 'tag:iframe' or an integer
        to be used as the index where the first index starts at 1.

        Will return None if the method passed to it has NoReturn.

        See `find_element` method in `_base.py` for ``frame_locator`` and
        ``element_locator`` usage/syntax

        :param frame_locator: WebElement, str or int - locator of the frame.
        :param element_locator: WebElement or str - Locator of the searched
            element within the frame.
        :param method:
        :return: WebElement or NoSuchElementException
        """
        self.switch_to_frame(frame_locator)
        self.log.info('Sending method `{}` to element `{}`'.format(
            method, element_locator))
        to_return = method(element_locator)
        self.driver.switch_to.default_content()
        return to_return

    def switch_to_frame(self, locator_or_index):
        """
        Sets frame identified by ``locator_or_index`` as the current frame.
        The `locator` can be a string such as 'tag:iframe' or an integer to be
        used as the index where the first index starts at 1.

        Works both with frames and iframes. Use `Unselect Frame` to cancel
        the frame selection and return to the main frame.

        See `find_element` method in `_base.py` for ``locator_or_index``
        usage/syntax

        :param locator_or_index: WebElement, str or int
        :return: NoReturn
        """
        self.log.info("Selecting frame '%s'." % locator_or_index)
        if isinstance(locator_or_index, int):
            locator = locator_or_index - 1
        else:
            # get element if the locator is not an integer
            locator = self.find_element(locator_or_index)
        self.driver.switch_to.frame(locator)

    def unselect_frame(self):
        """
        Sets the main frame as the current frame.
        """
        self.driver.switch_to.default_content()
