from config import *

# external

# internal
from ..logger import Logger
from .base import Base


class Frames(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def send_method_to_element_in_frame(self, frame_locator, element_locator, method):
		"""
		Perform a Browser method on an element inside of a frame without having
		switch in and out of the frame.
		Will return None if the method passed to it has NoReturn

		:param frame_locator: WebElement or str - locator of the frame.
		:param element_locator: WebElement or str - Locator of the searched
			element within the frame.
		:param method:
		:return: WebElement or NoSuchElementException
		"""
		frame = self.find_element(frame_locator)
		self.driver.switch_to.frame(frame)
		self.log.info('Getting {} from {}'.format(element_locator, frame_locator))
		to_return = method(element_locator)
		self.driver.switch_to.default_content()
		return to_return

	def select_frame(self, locator):
		"""
		Sets frame identified by ``locator`` as the current frame.

		Works both with frames and iframes. Use `Unselect Frame` to cancel
		the frame selection and return to the main frame.

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info("Selecting frame '%s'." % locator)
		element = self.find_element(locator)
		self.driver.switch_to.frame(element)

	def unselect_frame(self):
		"""
		Sets the main frame as the current frame.
		"""
		self.driver.switch_to.default_content()