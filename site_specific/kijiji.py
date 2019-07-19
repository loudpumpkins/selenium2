from ..config import *

# external
from typing import Any, Callable, List, NamedTuple, NoReturn, Union as U, Tuple

# internal
from ..browser import Browser
from ..logger import Logger

class Kijiji:

	# good format to fetch all locations
	locations_access = 'https://web.archive.org/web/20170914180512/https://www.kijiji.ca/'

	category_page = 'https://www.kijiji.ca/p-post-ad.html?categoryId={}'
	my_ads = 'https://www.kijiji.ca/m-my-ads/active/1'
	my_favourites = 'https://www.kijiji.ca/m-watch-list.html'
	my_messages = 'https://www.kijiji.ca/m-msg-my-messages/'
	my_orders = 'https://www.kijiji.ca/t-my-orders.html'
	my_profile = 'https://www.kijiji.ca/o-profile/1017207992/1'
	my_settings = 'https://www.kijiji.ca/t-settings.html'
	sign_in_page = 'https://www.kijiji.ca/t-login.html'

	def __init__(self, driver: U[Browser,str], desired_capabilities: dict = None,
	             profile: object = None, options: object = None):
		self.log = Logger().log
		if type(driver) is Browser:
			self.driver = driver
		elif type(driver) is str:
			self.driver = Browser(driver, desired_capabilities, profile, options)
		else:
			raise ValueError('Expected for driver to be of type "string" or '
			                 '"Browser", but received a type of "%s" instead'
			                 % (type(driver),))

	def active_posts(self)->int:
		"""
		Returns the number of active ads as displayed by kijiji - alternative way
		to count active ads instead of using len(_.get_active_posts_ids())

		:return: int
		"""
		active = self.driver.find_element(
			'//button[@id="active"]/div/'
			'span[starts-with(@class,"filterButtonCounter-")]')
		return int(active.text)

	def delete_all_ads(self)->bool:
		"""
		Attempts to delete all ads and returns True of None are left
		regardless of if any were active or not and False otherwise.
			Steps:
			  (1) - Go to my ads
			  (2) - Select all active ads
			  (3) - Iterate through the ads and click the `Delete` link
			  (4) - Assert `deleted successfully` message
			  (5) - Go to my ads again and see if any are active

		:return: bool
		"""
		if not self.is_signed_in():
			raise RuntimeError('Attempted to delete all ads, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads) #(1)
		ads = self.driver.find_elements('//li[starts-with(@class,"item")]') #(2)
		self.log.info("Deleting all ads.")
		for ad in ads:
			self.driver.find_element('.//button[starts-with(@class,"actionLink-")]',
			                         parent=ad).click() #(3)
			response = self.driver.wait_for_element( #(4)
				'.//div[contains(@class,"container__success")]/*[starts-with(@class,"messageTitle")]',
				parent=ad)
			self.log.info("Deleted an ad. Kijiji [SUCCESS] msg: %s"
			              % response.text)
		self.driver.goto(self.my_ads)  #(5)
		return self.driver.wait_for_page_to_contain('have no active ads')


	def delete_oldest_ad(self)->str:
		"""
		Deletes only the oldest ad and returns the ID of the ad as a str or
		None if failed.
			Steps:
			  (1) - Go to my ads
			  (2) - Select all active ads
			  (3) - Select and click the `delete` link of the last ad
			  (4) - Assert `deleted successfully` message

		:return: str - the ID of the ad deleted
		"""
		if not self.is_signed_in():
			raise RuntimeError('Attempted to delete oldest ad, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads) #(1)
		self.driver.wait_for_element('//li[starts-with(@class,"item")]')
		ads = self.driver.find_elements('//li[starts-with(@class,"item")]') #(2)
		if ads:
			raw_id = ads[-1].get_attribute('data-qa-id')
			ad_id = "".join(filter(str.isdigit, raw_id)) # remove prefix 'ad-id-...'
			self.driver.wait_for_element('.//button[starts-with(@class,"actionLink-")]',
			                         parent=ads[-1]).click() #(3)
			self.log.info('Deleting oldest ad. ID: %s' % ad_id)
			response = self.driver.wait_for_element( #(4)
				'.//div[contains(@class,"container__success")]/*[starts-with(@class,"messageTitle")]',
				parent=ads[-1])
			self.log.info("Deleted oldest add. Kijiji [SUCCESS] msg: %s"
			              % response.text)
			return ad_id
		else:
			self.log.info('Attempting to delete the oldest ad, but none were '
			              'found.')
			return None

	def get_active_posts_ids(self)->List[str]:
		"""
		Get a list of active IDs from MyAds page.
		:return: List[str]
		"""
		if not self.is_signed_in():
			raise RuntimeError('Attempted to count active posts, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads)
		ads = self.driver.find_elements('//li[starts-with(@class,"item")]')
		ids = []
		for ad in ads:
			raw_id = ad.get_attribute('data-qa-id')
			ad_id = "".join(filter(str.isdigit, raw_id)) #extract the ID
			ids.append(ad_id)
		return ids

	def get_new_messages(self)->List[str]:
		pass

	def is_signed_in(self)->bool:
		"""
		Will look for notifications icon (the bell) which is available only if
		the user is logged in
		To assert that user is signed out, use "is_signed_out()" method as it
		is faster.

		:return: bool - True for logged in
		"""
		try:
			self.driver.wait_for_element("//button[starts-with(@class,'cont')]")
			self.log.info('Asserted user is logged in.')
			return True
		except:
			self.log.info('Failed to assert that the user is logged in.')
			return False

	def is_signed_out(self)->bool:
		"""
		Will look for 'Sign in' link in the nav bar which is available only if
		the user is logged out
		To assert that user is signed in, use "is_signed_in()" method as it
		is faster.

		:return: bool - True for logged out
		"""
		try:
			self.driver.wait_for_element("@Sign In")
			self.log.info('Asserted user is logged out.')
			return True
		except:
			self.log.info('Failed to assert that the user is logged out.')
			return False

	def log_alert_message(self)->NoReturn:
		"""Get the alert displayed by kijiji, such as invalid login"""

		# get error message (login page)
		alert_banner = self.driver.find_element(
			'//div[@id="MessageContainer"]//div[@class="message"]',
			required=False
		)
		if alert_banner is not None:
			error = self.driver.find_element(
				'//div[@id="MessageContainer"]/div[contains(@class,"error")]',
				required=False,
			)
			if error is not None:
				self.log.info('Kijiji [ERROR] msg: %s' % (alert_banner.text,))
			else:
				self.log.info('Kijiji msg: %s' % (alert_banner.text,))

		# get error message from images upload
		alert_banner = self.driver.find_element(
			'//span[@class="field-message error"]',
			required=False
		)
		if alert_banner is not None:
			self.log.info('Kijiji [ERROR] msg: %s'
			              % (alert_banner.get_attribute('innerHTML'),))

		# get success message found at top of page (common, in post success too)
		alert_banner = self.driver.find_element(
			'//div[contains(@class,"container__success")]/*[starts-with(@class,"messageTitle")]',
			required=False
		)
		if alert_banner is not None:
			self.log.info('Kijiji [SUCCESS] msg: %s' % (alert_banner.text,))

	def new_messages(self)->int:
		pass

	def post_ad(self, data: dict):
		pass

	def reply_to_new_messages(self)->NoReturn:
		pass

	def sign_in(self, username:str, password:str)->NoReturn:
		"""
		Sign in to kijiji using the provided username and password.
		If the user is already signed in and it can be confirmed, the process
		will not be halted, however, in the event that a sign in cannot be
		confirmed, the process will be halted and will throw a RuntimeError
		exception.

		:param username: str
		:param password: str
		:return: NoReturn
		"""
		self.driver.goto(self.sign_in_page)
		if self.is_signed_out():
			self.log.info("Signing in to kijiji.")
			self.driver.send_keys('#LoginEmailOrNickname', username)
			self.driver.send_keys('#login-password', password)
			self.driver.click_button('#SignInButton')
			if not self.is_signed_in(): #failed confirm sign in
				self.log_alert_message()
				raise RuntimeError('Failed to sign in using id: "%s", pw: "%s".'
				                   % (username, password))
		else: #failed to confirm user is signed out
			if self.is_signed_in():
				self.log.info("Attempted to sign in, but the user is already "
				              "signed in.")
			else: #failed to confirm user is also signed in
				self.log.critical('Failed to assert that user is either '
				                  'signed in or signed out while trying to '
				                  'sign in. Site might have changed. User '
				                  'used: %s, password: %s'
				                  % (username, password))
				raise RuntimeError('Failed assert that the user is either '
				                   'signed in or signed out.')

	def sign_out(self)->NoReturn:
		"""
		Sign out from kijiji.
		If the user is already signed out and it can be confirmed, the process
		will not be halted, however, in the event that a sign out cannot be
		confirmed, the process will be halted and will throw a RuntimeError
		exception.

		:return: NoReturn
		"""
		url = self.driver.get_url()
		self.log.info("Signing out of kijiji.")
		if 'www.kijiji.ca' not in url:
			self.driver.goto(self.my_settings)
		if self.is_signed_in():
			dropdown = self.driver.wait_for_element("//button[contains(@class,'control')]")
			dropdown.click()
			logout = self.driver.wait_for_element("//button[contains(@class,'signOut')]")
			logout.click()
			if not self.is_signed_out():
				raise RuntimeError('Failed to sign out.')
			self.log_alert_message()
		else:
			if self.is_signed_out():
				self.log.info("Attempted to sign out, but the user is already "
				              "signed out.")
			else:
				self.log.critical('Failed to assert that user is either '
				                  'signed in or signed out while trying to '
				                  'sign out. Site might have changed.')
				raise RuntimeError('Failed assert that the user is either '
				                   'signed in or signed out.')

	def _post_success(self)->bool:
		#log URL to analyse behaviour for now, might change success criteria to
		#be based on the URL if it is consistent.
		url = self.driver.get_url()
		if 'posted=true' not in url and 'Activated=true' not in url:
			self.log.critical("URL's GET variables 'posted' or 'activated' "
			                  "where not set to TRUE by Kijiji.\nFull url: %s"
			                  % url)
		return self.driver.wait_for_page_to_contain(
			'You have successfully posted your ad')
