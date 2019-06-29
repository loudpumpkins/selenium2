from ..config import *

# external
from collections import namedtuple
import re
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
import time

# internal
from ..logger import Logger
from ._driver import Driver

WindowInfo = namedtuple('WindowInfo', 'handle, id, name, title, url')

class WindowManager(Driver):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log
		self._selectors = {
			'default': self._select_by_default,
			'id': self._select_by_id,
			'name': self._select_by_name,
			'title': self._select_by_title,
			'url': self._select_by_url,
		}

	def select_window(self, locator, timeout=DEFAULT_TIMEOUT):
		"""
		Selects browser window matching ``locator`` where "window" is a pop-up
		or a tab opened in the current session.

		- The ``locator`` can be specified to use an explicit strategy, namely:
		  'name', 'id', 'title', 'url' exp: _.select_window('id=12')

		- By default, the `locator` is matched against the following
		  window properties (in the shown order).
			# 1- handle ID (set by selenium)
			# 2- window id (can be set by user with JavaScript)
			# 3- window name (can be set by user with JavaScript)
			# 4- page title
			# 5- page url

        - If the ``locator`` is ``NEW`` (case-insensitive), the latest
          opened window is selected. It is an error if this is the same
          as the current window.

        - If the ``locator`` is ``MAIN`` (default, case-insensitive),
          the main window is selected.

        - If the ``locator`` is ``CURRENT`` (case-insensitive), nothing is
          done. This effectively just returns the current window handle.

        - If the ``locator`` is not a string, it is expected to be a list
          of window handles _to exclude_. Such a list of excluded windows
          can be get from `Get Window Handles` prior to doing an action that
          opens a new window.

		The ``timeout`` is used to specify how long keyword will poll to select
        the new window.

		Returns the current window handle or raises NoSuchWindowException

		:param locator: str or List[handles]
		:param timeout: int
		:return: current window handle if available
		"""
		epoch = time.time()
		timeout = timeout + epoch
		return self._select(locator, timeout)

	def close_window(self):
		"""Closes currently opened pop-up window."""
		self.log.info('Closing current active window.')
		self.driver.close()

	def get_all_windows_handles(self):
		"""
		Return all current window handles as a list.
		Can be used as a list of windows to exclude with `Select Window`.
		"""
		self.log.info('Getting all window`s handles.')
		return self.driver.window_handles

	def get_all_windows_ids(self):
		"""Returns id attributes of all known browser windows."""
		self.log.info('Getting all window`s ids')
		return [info.id for info in self._get_all_windows_infos()]

	def get_all_windows_names(self):
		"""Returns names of all known browser windows."""
		self.log.info('Getting all window`s names')
		return [info.name for info in self._get_all_windows_infos()]

	def get_all_windows_titles(self):
		"""Returns titles of all known browser windows."""
		self.log.info('Getting all window`s titles.')
		return [info.title for info in self._get_all_windows_infos()]

	def get_all_windows_urls(self):
		"""Returns and logs URLs of all known browser windows."""
		self.log.info('Getting all window`s urls.')
		return [info.url for info in self._get_all_windows_infos()]

	def get_window_handle(self):
		"""Returns the current window handle"""
		self.log.info('Getting current window`s handle')
		return self.driver.current_window_handle

	def get_window_info(self):
		"""
		Returns all current window's info as a named tupple
		namedtuple('WindowInfo', 'handle, id, name, title, url')
		:return: NamedTuple
		"""
		self.log.info('Getting window info.')
		return self._get_current_window_info()

	def get_window_position(self):
		"""
		Returns current window position.

		Position is relative to the top left corner of the screen. Returned
		values are integers.

		:return: Tuple[x: int, y: int]
		"""
		self.log.info('Getting window position.')
		position = self.driver.get_window_position()
		return position['x'], position['y']

	def get_window_size(self):
		"""
		Returns current window width and height as a tuple of ints.
		:return: Tuple [width: int, height: int]
		"""
		self.log.info('Getting window size.')
		size = self.driver.get_window_size()
		return size['width'], size['height']

	def maximize_browser_window(self):
		"""Maximizes current browser window."""
		self.driver.maximize_window()

	def set_window_id(self, id):
		"""
		Assigns an ID to the current window

		:param id: int or str
		:return: NoReturn
		"""
		self.log.info('Setting window id to "{}"'.format(id))
		self.driver.execute_script('window.id = "{}";'.format(id))

	def set_window_name(self, name):
		"""
		Assign a name to the current window

		:param name: int or str
		:return: NoReturn
		"""
		self.log.info('Setting window name to "{}"'.format(name))
		self.driver.execute_script('window.name = "{}";'.format(name))

	def set_window_position(self, x, y):
		"""
		Sets window position using ``x`` and ``y`` coordinates.

		The position is relative to the top left corner of the screen,
		but some browsers exclude possible task bar set by the operating
		system from the calculation. The actual position may thus be
		different with different browsers.

		Values can be given using strings containing numbers or by using
		actual numbers. See also `Get Window Position`.

		:param x: str or int
		:param y: str or int
		:return: NoReturn
		"""
		self.log.info('Setting window position to x:{} and y:{}.'.format(x,y))
		self.driver.set_window_position(int(x), int(y))

	def set_window_size(self, width, height):
		"""
		Sets current windows size to given ``width`` and ``height``.

		Values can be given using strings containing numbers or by using
		actual numbers. See also `Get Window Size`.

		Browsers have a limit how small they can be set. Trying to set them
		smaller will cause the actual size to be bigger than the requested
		size.

		:param width: str or int
		:param height: str or int
		:return: NoReturn
		"""
		self.log.info('Setting window size to width:{} and height:{}.'.format(
			width, height
		))
		return self.driver.set_window_size(int(width), int(height))

	####################################################
	###    Functions used mostly by select_window()   ##
	####################################################
	# main selector
	def _select(self, locator, timeout):
		while True:
			try:
				if isinstance(locator, list):
					return self._select_excluded(locator)
				elif locator.upper() == 'CURRENT':
					# return current handle and do nothing
					return self.get_window_handle()
				elif locator.upper() == 'MAIN':
					return self._select_main_window()
				elif locator.upper() == 'NEW':
					return self._select_last_index()
				else:
					strategy, locator = self._get_selector(locator)
					return self._selectors[strategy](locator)
			except NoSuchWindowException:
				if time.time() > timeout:
					raise
				time.sleep(0.2)

	# parser
	def _get_selector(self, locator):
		groups = re.search('^ ?(\w+) ?[:=] ?(.+)', locator)
		# parse locator into "selector" and "element"
		# 'name = spicy' returns 'name' and 'spicy'
		if groups is None:
			return 'default', locator
		selector = groups.group(1)
		element = groups.group(2)
		if selector in self._selectors:
			return selector, element
		return 'default', locator

	# selector
	def _select_excluded(self, excludes):
		try:
			current_handle = self.get_window_handle()
		except NoSuchWindowException:
			current_handle = None
		self.log.info('Switching to a window excluded from {}.'.format(excludes))
		for handle in self.driver.window_handles:
			if handle not in excludes:
				self.driver.switch_to.window(handle)
				return current_handle
		raise NoSuchWindowException('No window not matching excludes %s found.'
		                     % excludes)

	# selector
	def _select_main_window(self):
		try:
			current_handle = self.get_window_handle()
		except NoSuchWindowException:
			current_handle = None
		self.log.info('Switching to main window.')
		handles = self.driver.window_handles
		self.driver.switch_to.window(handles[0])
		return current_handle

	# selector
	def _select_last_index(self):
		try:
			current_handle = self.get_window_handle()
		except NoSuchWindowException:
			current_handle = None
		handles = self.driver.window_handles
		self.log.info('Switching to new window.')
		if handles[-1] == self.driver.current_window_handle:
			raise NoSuchWindowException('Window with last index is same as '
			                     'the current window.')
		self.driver.switch_to.window(handles[-1])
		return current_handle

	# selector
	def _select_by_default(self, criteria):
		try:
			starting_handle = self.get_window_handle()
		except NoSuchWindowException:
			starting_handle = None
		for handle in self.driver.window_handles:
			# iterate through each window
			self.driver.switch_to.window(handle)
			for item in self._get_current_window_info():
				# Check for match in the following order:
				# 1- handle ID (set by selenium)
				# 2- window id (can be set by user with JavaScript)
				# 3- window name (can be set by user with JavaScript)
				# 4- page title
				# 5- page url
				if item == criteria:
					# return on first match
					return starting_handle
		if starting_handle:
			# go back to starting window in case of failure and raise exception
			self.driver.switch_to.window(starting_handle)
		raise NoSuchWindowException("No window matching handle, id, name, title "
		                            "or URL '%s' found." % criteria)

	# selector
	def _select_by_id(self, id):
		self.log.info('Switching to window with id "{}".'.format(id))
		return self._select_by_matcher(
			lambda window_info: window_info.id == id,
			"Unable to locate window with id '%s'." % id
		)

	# selector
	def _select_by_name(self, name):
		self.log.info('Switching to window with name "{}".'.format(name))
		return self._select_by_matcher(
			lambda window_info: window_info.name == name,
			"Unable to locate window with name '%s'." % name
		)

	# selector
	def _select_by_title(self, title):
		self.log.info('Switching to window with page title "{}".'.format(title))
		return self._select_by_matcher(
			lambda window_info: window_info.title == title,
			"Unable to locate window with title '%s'." % title
		)

	# selector
	def _select_by_url(self, url):
		self.log.info('Switching to window with url "{}".'.format(url))
		return self._select_by_matcher(
			lambda window_info: window_info.url == url,
			"Unable to locate window with URL '%s'." % url
		)

	# selector support
	def _select_by_matcher(self, matcher, error):
		try:
			starting_handle = self.get_window_handle()
		except NoSuchWindowException:
			starting_handle = None
		for handle in self.driver.window_handles:
			self.driver.switch_to.window(handle)
			if matcher(self._get_current_window_info()):
				return starting_handle
		if starting_handle:
			self.driver.switch_to.window(starting_handle)
		raise NoSuchWindowException(error)

	def _get_current_window_info(self):
		try:
			id, name = self.driver.execute_script(
				"return [ window.id, window.name ];")
		except WebDriverException:
			# The webdriver implementation doesn't support Javascript so we
			# can't get window id or name this way.
			id = name = None
		return WindowInfo(self.driver.current_window_handle,
		                  id if id is not None else 'undefined',
		                  name or 'undefined',
		                  self.driver.title or 'undefined',
		                  self.driver.current_url or 'undefined')

	####################################################
	###                      END                      ##
	####################################################

	def _get_all_windows_infos(self):
		infos = []
		try:
			starting_handle = self.get_window_handle()
		except NoSuchWindowException:
			starting_handle = None
		try:
			for handle in self.driver.window_handles:
				self.driver.switch_to.window(handle)
				infos.append(self._get_current_window_info())
		finally:
			if starting_handle:
				self.driver.switch_to.window(starting_handle)
		return infos