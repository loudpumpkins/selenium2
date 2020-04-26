from ..config import *

# external
import os, pickle

# internal
from ..logger import Logger
from ._base import Base


class Cookies(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def add_cookie(self, cookie_dict):
		"""
		Adds a cookie to your current session.

		Usage:
			self.add_cookie({‘name’ : ‘foo’, ‘value’ : ‘bar’})
			self.add_cookie({‘name’ : ‘foo’, ‘value’ : ‘bar’, ‘path’ : ‘/’})
			self.add_cookie(
				{‘name’ : ‘foo’, ‘value’ : ‘bar’, ‘path’ : ‘/’, ‘secure’:True}
			)

		:param cookie_dict: A dictionary object, with required keys - “name” and “value”;
				optional keys - “path”, “domain”, “secure”, “expiry”
		:return: NoReturn
		"""
		self.driver.add_cookie(cookie_dict)

	def delete_all_cookies(self):
		"""
        Delete all cookies in the scope of the session.

		:return: NoReturn
		"""
		self.driver.delete_all_cookies()

	def delete_cookie(self, name: str):
		"""
		Deletes a single cookie with the given name.

		:param name: str - cookie name
		:return: NoReturn
		"""
		self.driver.delete_cookie(name)

	def get_cookie(self, name:str):
		"""
		Get a single cookie by name. Returns the cookie if found, None if not.

		:param name: str - cookie name
		:return: dict or None
		"""
		return self.driver.get_cookie(name)

	def get_cookies(self):
		"""
		Returns a set of dictionaries, corresponding to cookies visible in the
		current session.

		:return: List[dict]
		"""
		return self.driver.get_cookies()

	def load_cookies(self, filename: str, path: str='default'):
		"""
		Load all cookies stored in `filename` into the current browser session.
		Will look for the file in the DEFAULT_COOKIE_DIRECTY if the `path` is
		set to `default` or will look in the specified `path` if one is provided.

		`filename` must be a binary data steam.

		:param filename: str - filename
		:param path:
		:return:
		"""
		if path == 'default':
			path = os.path.join(self._root.cookies_directory, filename)
		else:
			path = os.path.join(path, filename)
		try:
			with open(path, 'rb') as filehandle:
				# load binary data steam of a list of cookies
				cookies = pickle.load(filehandle)
		except FileNotFoundError:
			raise RuntimeError("Failed to load file '%s'. File not found. "
			                   "Full path used: %s" % (filename, path) )
		for cookie in cookies:
			if 'expiry' in cookie:
				del cookie['expiry']
			self.driver.add_cookie(cookie)

	def save_cookies(self, filename):
		"""
		Save all current browser's cookies to set `filename` and return the path
		of the file.

		``filename`` argument specifies the name of the file to write the
		cookies into. The directory where cookies are saved can be set with
		`set_screenshot_directory`. Default path is in the config file.

		An absolute path to the created cookies file is returned.

		:param filename: str - desired filename
		:return: str - the file's full path
		"""
		if not self.driver.session_id:
			self.log.info('Cannot save cookies because no browser is open.')
			return
		path = self._get_cookies_path(filename)
		self._create_directory(path)
		cookies = self.driver.get_cookies()
		with open(path, 'wb') as filehandle:
			# store the cookies as binary data stream
			pickle.dump(cookies, filehandle)
		self.log.info('Saving cookies to {}'.format(path))
		return path

	def set_cookies_directory(self, path=None, append=True):
		"""
		Sets the directory for saved cookies.

		``path`` can be an absolute path or relative path from the current
		cookies_directory. If the directory does not exist, it will be
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
		previous = self._root.cookies_directory
		path = os.path.abspath(path)
		self.log.info('Setting cookies directory from {} to {}'.format(
			previous, path
		))
		self._root.cookies_directory = path
		return previous

	def set_cookies_expiry(self, date: int = 3735325880):
		"""
		Sets the expiry date of all cookies to 'date'. Default is 3735325880
		which is equivalent to Thu, 13 May 2088 22:38:37 GMT.

		Will load all cookies into memory, delete cookies, set date and set
		new cookies with new expiry date.

		:param date: int - the expiry date
		:return: NoReturn
		"""
		cookies = self.driver.get_cookies()
		self.driver.delete_all_cookies()
		for cookie in cookies:
			cookie['expiry'] = date
			self.driver.add_cookie(cookie)

	def _create_directory(self, path):
		target_dir = os.path.dirname(path)
		if not os.path.exists(target_dir):
			self.log.info('Creating new directory to store cookies at {}'.format(
				target_dir
			))
			os.makedirs(target_dir)

	def _get_cookies_path(self, filename):
		directory = self._root.cookies_directory
		filename = filename.replace('/', os.sep)
		return os.path.join(directory, filename)