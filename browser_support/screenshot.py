from ..config import *

# external
import os

# internal
from ..logger import Logger
from ._base import Base


class Screenshot(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def capture_element_screenshot(self, locator,
	                               filename='element-screenshot-{index:03}.png'):
		"""
		Captures screenshot of the element identified by ``locator``.

		See `capture_page_screenshot()` for details about ``filename`` argument.
		An absolute path to the created element screenshot is returned.

		Support for capturing the screenshot from a element has limited support
		among browser vendors. Please check the browser vendor driver documentation
		does the browser support capturing a screenshot from a element.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param filename: str - desired filename
		:return: str - the file's full path
		"""
		if not self.driver.session_id:
			self.log.info(
				'Cannot capture screenshot from element because no browser is open.')
			return
		path = self._get_screenshot_path(filename)
		self._create_directory(path)
		element = self.find_element(locator, required=True)
		if not element.screenshot(path):
			raise RuntimeError(
				"Failed to save element screenshot '{}'.".format(path))
		self.log.info('Saving screenshot at {}'.format(path))
		return path

	def capture_page_screenshot(self, filename='screenshot-{index:03}.png'):
		"""
		Takes screenshot of the current page and return the path of the file.

		``filename`` argument specifies the name of the file to write the
		screenshot into. The directory where screenshots are saved can be
		set when `set_screenshot_directory`. Default path is in the config file.

		``filename`` contains marker ``{index}``, it will be automatically
		replaced with unique running index preventing files to be overwritten.
		Indices start from 1, but it can be omitted.

		An absolute path to the created screenshot file is returned.

		:param filename: str - desired filename
		:return: str - the file's full path
		"""
		if not self.driver.session_id:
			self.log.info('Cannot capture screenshot because no browser is open.')
			return
		path = self._get_screenshot_path(filename)
		self._create_directory(path)
		if not self.driver.save_screenshot(path):
			raise RuntimeError("Failed to save screenshot '{}'.".format(path))
		self.log.info('Saving screenshot at {}'.format(path))
		return path

	def set_screenshot_directory(self, path=None, append=True):
		"""
		Sets the directory for captured screenshots.

		``path`` can be an absolute path or relative path from the current
		screenshot_directory. If the directory does not exist, it will be
		created.

		``append`` is set to True by default and will append to current path and
		normalise it, where False will overwrite the path attribute.

		Will return the previous path to be stored and re-set if needed.

		:param path: str - the path to append or set
		:param append: bool - True will add / False will replace
		:return: str - previous path
		"""
		if path is not None:
			path = os.path.normpath(os.path.join(self._root.screenshot_directory, path))\
				if append else path
			self._create_directory(path)
		previous = self._root.screenshot_directory
		path = os.path.abspath(path)
		self.log.info('Setting screenshot directory from {} to {}'.format(
			previous, path
		))
		self._root.screenshot_directory = path
		return previous

	def _create_directory(self, path):
		target_dir = os.path.dirname(path)
		if not os.path.exists(target_dir):
			self.log.info('Creating new directory to store screenshots at {}'.format(
				target_dir
			))
			os.makedirs(target_dir)

	def _get_screenshot_path(self, filename):
		directory = self._root.screenshot_directory
		filename = filename.replace('/', os.sep)
		index = 0
		while True:
			index += 1
			formatted = filename.format(index=index)
			path = os.path.join(directory, formatted)
			# filename didn't contain {index} or unique path was found
			if formatted == filename or not os.path.exists(path):
				return path