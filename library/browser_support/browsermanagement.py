from config import *

# external
import re

# internal
from ..logger import Logger
from .base import Base

class BrowserManagement(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def back(self):
		""" Simulates a back button click """
		self.driver.back()

	def forward(self):
		""" Simulates a forward button click """
		self.driver.forward()

	def refresh(self):
		""" Refreshes current page """
		self.driver.refresh()

	def close_browser(self):
		""" Close all windows and tabs associated with the session """
		self.log.info('Closing browser with session id {}.'
		               .format(self.driver.session_id))
		self.driver.quit()

	def get_session_id(self):
		"""Returns the currently active browser's session id."""
		return self.driver.session_id

	def get_source(self):
		"""Returns the entire HTML source of the current page or frame."""
		return self.driver.page_source

	def get_title(self):
		"""Returns the title of current page."""
		return self.driver.title

	def get_url(self):
		"""Returns the current browser URL."""
		return self.driver.current_url

	def goto(self, url):
		"""Navigates the active browser instance to the provided url.
		Will append default prefix to the url if it's missing"""
		if not re.search(r'^https?://', url):
			url = 'https://' + url
		self.log.info("Opening url '%s'" % url)
		self.driver.get(url)