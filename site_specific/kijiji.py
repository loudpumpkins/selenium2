from ..config import *

# external
from selenium.common.exceptions import TimeoutException
from typing import Any, Callable, List, NamedTuple, NoReturn, Union as U, Tuple
from time import sleep

# internal
from ..browser import Browser
from ..logger import Logger
from ..site_specific import DefaultBehaviour


class Kijiji(DefaultBehaviour):
	# good format to fetch all locations
	locations_access = 'https://web.archive.org/web/20170914180512/https://www.kijiji.ca/'

	homepage = 'https://www.kijiji.ca/'
	category_page = 'https://www.kijiji.ca/p-post-ad.html?categoryId={}'
	my_ads = 'https://www.kijiji.ca/m-my-ads/active/1'
	my_favourites = 'https://www.kijiji.ca/m-watch-list.html'
	my_messages = 'https://www.kijiji.ca/m-msg-my-messages/'
	my_orders = 'https://www.kijiji.ca/t-my-orders.html'
	my_profile = 'https://www.kijiji.ca/o-profile/1017207992/1'
	my_settings = 'https://www.kijiji.ca/t-settings.html'
	select_category = 'https://www.kijiji.ca/p-post-ad.html?categoryId={}'
	select_location = 'https://www.kijiji.ca/b-buy-sell/guelph/c10l{}'
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

	def delete_ad_with_id(self, ad_id:Any)->bool:
		"""
		Delete ad with a specific id.

			Steps:
			  (1) - Go to my ads
			  (2) - Order ads by oldest first
			  (3) - Select all active ads
			  (4) - Iterate through the elements to find the ad with `id`
			  (5) - Delete the ad

		:param ad_id: int
		:return: bool (True for success, False otherwise)
		"""
		self.log.info('Deleting ad with id ["%s"].' % ad_id)
		if not self.is_signed_in():
			raise RuntimeError('Attempted to delete oldest ad, but the user is '
			                   'not signed in. You must sign in first.')
		self.driver.goto(self.my_ads)  # (1)
		try:
			self._sort_my_ads() # (2)
			self.driver.wait_for_element(
				'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]')
		except Exception as e:
			self.log.info('Unable to sort ads [no ads in My Ads]: ' + str(e).replace('\n', ''))
			return False
		ads = self.driver.find_elements(
			'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]')  # (3)
		for ad in ads: # (4)
			if str(ad_id) in ad.get_attribute('data-qa-id'):
				self.driver.wait_for_element(
					'.//button[starts-with(@class,"actionLink-")]',
					parent=ad).click() # (5)
				self.log.info("Deleted ad with ID: [%s]."
				              % ad_id)
				return True
		self.log.info('Failed to delete ad id ["%s"]. Not found.' % ad_id)
		return False

	def delete_all_ads(self, previous:int = -1)->bool:
		"""
		Attempts to delete all ads and returns True if None are left
		regardless of if any were active or not or Raise exception otherwise.
			Steps:
			  (1) - Go to my ads
			  (2) - Select all active ads
			  (3) - Iterate through the ads and click the `Delete` link
			  (4) - Go to my ads again and see if any are active

		:return: bool
		"""
		if not self.is_signed_in():
			raise RuntimeError('Attempted to delete all ads, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads) #(1)
		self.driver.wait_for_element(
			'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]')
		ads = self.driver.find_elements(
			'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]') # (2)
		if ads == previous: # prevents infinite recursion
			raise RuntimeError('Attempted to delete all ads, but recursion has '
			                   'no effect on number of ads left. (infinite recursion)')
		self.log.info("Deleting all ads [%s total]." % len(ads))
		for ad in ads:
			self.log.info("Deleted an ad.")
			self.driver.wait_for_element('.//button[starts-with(@class,"actionLink-")]',
			                         parent=ad).click() #(3)
			sleep(2)
		self.driver.goto(self.my_ads)  #(4)
		try:
			return self.driver.wait_for_page_to_contain('have no active ads')
		except TimeoutException:
			return self.delete_all_ads(len(ads))

	def delete_oldest_ad_of_category(self, user_bread_crumbs:str)->bool:
		"""
		Delete the oldest ad within a specific category. The category is
		identified via the user bread crumbs.

		 Bread Crumbs examples:
		   - example: "Buy & Sell > Furniture > Coffee Tables"
		   - user:    "Buy & Sell > Furniture > Coffee Tables Change category"

			Steps:
			  (1) - Go to my ads
			  (2) - Order ads by oldest first
			  (3) - Select all active ads
			  (4) - Iterate through the ads to find the AdId of the oldest ad
			  (5) - Call delete_ad_with_id()

		:param bread_crumbs: str - "Buy & Sell > Furniture > Coffee Tables"
		:return: str - the ID of the ad deleted
		"""
		self.log.info('Deleting oldest ad with the category: ["%s"].'
		              % user_bread_crumbs)
		if not self.is_signed_in():
			raise RuntimeError('Attempted to delete oldest ad, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads) #(1)
		try:
			self._sort_my_ads() #(2)
			self.driver.wait_for_element(
				'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]')
		except Exception as e:
			self.log.info(
				'Unable to sort ads [no ads in My Ads]: ' + str(e).replace('\n',''))
			return False
		ads = self.driver.find_elements(
			'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]') #(3)
		urls:List[Tuple] = [] #('href','adId')
		for ad in ads: # (4)
			href = self.driver.wait_for_element(
				parent=ad,
				locator=".//a[starts-with(@class,'actionLink')]"
			).get_attribute('href')
			raw_id = ad.get_attribute('data-qa-id')
			ad_id = "".join(
				filter(str.isdigit, raw_id))  # remove prefix 'ad-id-...'
			urls.append((href,ad_id))
		for url in urls:
			self.driver.goto(url[0])
			current_bread_crumbs = self.driver.find_element(
				"//li[@class='category']/div[@class='form-section']").text
			if current_bread_crumbs	in user_bread_crumbs:
				return self.delete_ad_with_id(url[1]) # (5)

	def get_active_posts_ids(self)->List[str]:
		"""
		Get a list of active IDs from MyAds page.
		:return: List[str]
		"""
		if not self.is_signed_in():
			raise RuntimeError('Attempted to count active posts, but the user is '
			                   'not signed in.')
		self.driver.goto(self.my_ads)
		ads = self.driver.find_elements(
			'//ul[starts-with(@class,"list")]/li[starts-with(@class,"item")]')
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
		Will look for menu icon (profile avatar) which is available only if
		the user is logged in
		To assert that user is signed out, use "is_signed_out()" method as it
		is faster.

		:return: bool - True for logged in
		"""
		try:
			self.driver.wait_for_element("//button[starts-with(@class,'control-')]",
			                             timeout=40)
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
			self.driver.wait_for_element("@Sign In", timeout=40)
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

	def post_ad(self, details:List[dict], setup:dict, preview:bool=False)->str:
		"""
		Populate the post page with user's details, submit form and return the
		ad ID as a string.

		Steps:
		  (1) - Select user's location
		  (2) - Go to post page
		  (3) - Delete oldest ad if the user reached the post limit in
		        selected category
		  (4) - Upload all ad images
		  (5) - Populate user's details
		  (6) - Dismiss `select plan` and `policy` if present
		  (7) - Post or Preview the ad

		:param details: [{'name':[...], 'value':[...]}, [...]]
		:param setup: {
						'location_id': [...],
						'category_id': [...],
						'images_path': [...],
					  }
		:return:
		"""
		self._select_location(setup['location_id']) # (1)
		self._go_to_post_page(setup['category_id']) # (2)
		limit_message = self.driver.find_element(
			"//div[@id='PostingLimitMessage']//span[contains(@class,'tip-body')]",
			required=False
		)
		if limit_message is not None:
			limit_message = limit_message.text
			if 'You have reached your limit of' in limit_message: # (3)
				self.delete_oldest_ad_of_category(setup['bread_crumbs'])
				for e in range(5):
					self._go_to_post_page(setup['category_id'])
					limit_message = self.driver.find_element(
						"//div[@id='PostingLimitMessage']//span[contains(@class,'tip-body')]",
					).text
					if e == 4:
						raise RuntimeError( # limit message still present after trying 4 times
							'Category limit still maxed after deleting oldest ad.')
					elif 'You have reached your limit of' in limit_message:
						sleep(1)
						continue # limit message still present, wait a second and check again
					else:
						break # limit message removed, proceed
		self._upload_images(setup['images_path']) # (4)
		for detail in details:
			self._send_detail(detail) # (5)
		self._dismiss_obstacles() # (6)
		if preview: # (7)
			self._preview_post()
			self.log.info('Execution frozen - posted as `preview`.')
			sleep(9999)
		else:
			self._submit_post()
		self._assert_post_success()
		return self.driver.wait_for_element(
			'//a[starts-with(@class,"adId-")]').text

	def reply_to_new_messages(self)->NoReturn:
		pass

	def sign_in(self, username:str, password:str, cookies:str = None)->NoReturn:
		"""
		Sign in to Kijiji using the provided `username` and `password`.
		If a `cookies` filename is provided, it will try to load it and see if
		the user is now logged in.
		If the `cookies` filename is not found, it will try to sign in normally
		and save the `cookies` file after signing in.

		:param username: str
		:param password: str
		:param cookies: str
		:return: NoReturn
		"""
		if cookies is None:
			# no cookies filename provided or asked not to load cookie file
			self.driver.goto(self.sign_in_page)
			if self.is_signed_out():
				self.log.info("Signing in to kijiji without loading cookies.")
				self.driver.send_keys('#emailOrNickname', username)
				self.driver.send_keys('#password', password)
				self.driver.find_element("//label[@for='rememberMe']").click()
				self.driver.find_element("//button[starts-with(@class, 'signInButton')]").click()
				input("CAPTCHA completed? Press ENTER to continue.")
				if not self.is_signed_in(): #failed confirm sign in
					self.log_alert_message()
					raise RuntimeError('Failed to sign in using id: "%s", pw: "%s".'
					                   % (username, password))
				else:
					return #successfully logged in
			else: #failed to confirm user is signed out
				if self.is_signed_in():
					self.log.info("Attempted to sign in, but the user is already "
					              "signed in.")
					return  # successfully logged in
				else: #failed to confirm user is also signed in
					self.log.critical('Failed to assert that user is either '
					                  'signed in or signed out while trying to '
					                  'sign in. Site might have changed. User '
					                  'used: %s, password: %s'
					                  % (username, password))
					raise RuntimeError('Failed assert that the user is either '
					                   'signed in or signed out.')
		else:
			# try to load cookies and see if user is now logged in, or make cookies
			# if cookies file not found.
			self.driver.goto(self.homepage)
			self.log.info("Signing in to kijiji by loading cookies.")
			try:
				self.driver.load_cookies(cookies)
			except RuntimeError as e:
				self.log.info(e)
				self.sign_in(username, password)
				self.driver.save_cookies(cookies)
				return
			self.driver.goto(self.homepage)
			if self.is_signed_in():
				self.log.info("Cookies loaded and user is now logged in.")
				return
			else:
				self.log.info("Cookies loaded, but user is not logged in.")
				self.sign_in(username, password)
				self.driver.save_cookies(cookies)
				return

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
			self._dismiss_modal() # dismiss the 'enable notifications?' modal if it pops up
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

	def _dismiss_modal(self):
		"""Close kijiji modals requesting to turn notifications on"""
		modal = self.driver.find_element(
					'//button[@data-qa-id="ModalCloseButton"]', required=False)
		if modal is not None:
			modal.click() # dismiss

	def _dismiss_obstacles(self):
		"""Dismiss 'plan selection' and 'policy acknowledgement' if present"""
		term_confirmation = self.driver.find_element(
			"#PostAdConfirmationOfTerms",
			required=False
		)
		if term_confirmation is not None:
			self.driver.click_element("//label[@for='PostAdConfirmationOfTerms']")

		plan_selection = self.driver.find_element(
			"//button[starts-with(@data-qa-id,'package-0-bottom')]",
			required=False
		)
		if plan_selection is not None:
			self.driver.click_element(plan_selection)

	def _go_to_post_page(self, category_id:U[str, int])->NoReturn:
		"""
		Go to the category page to post ad in.
		:param category_id: int or str
		:return: NoReturn
		"""
		self.driver.log.info('Switching to post page of category ID: "%s"' % category_id)
		self.driver.goto(self.select_category.format(category_id))

	def _assert_post_success(self)->NoReturn:
		#log URL to analyse behaviour for now, might change success criteria to
		#be based on the URL if it is consistent.
		# self.driver.wait_for_page_to_contain('You have successfully posted your ad') # slow to respond
		url = self.driver.get_url()
		for e in range(6):
			if 'posted=true' not in url or 'adActivated=true' not in url:
				sleep(0.5)
				url = self.driver.get_url()
			else:
				return
		self.log.critical("URL's GET variables 'posted' or 'activated' "
		                  "where not set to TRUE by Kijiji.\nFull url: %s"
		                  % url)

	def _preview_post(self, attempts:int=1)->NoReturn:
		"""
		Try to preview form recursively for 4 seconds. Delays can occur after
		selecting a plan making the preview button temporarily unavailable.
		:param attempts: int
		:return: NoReturn
		"""
		if attempts <= 8:
			try:
				self.driver.simulate_event(
					'//button[@class="button-task secondary post-ad-button"]',
					'click'
				)
			except:
				sleep(0.5)
				self._preview_post(attempts+1)
		else:
			raise RuntimeError('Failed to preview form after %s attempts.'
			                   % attempts)

	def _select_location(self, location_id:U[str, int])->NoReturn:
		"""
		Change user location via URL change.
		:param location_id: str or int
		:return: NoReturn
		"""
		self.driver.log.info('Selecting user location: "%s"' % location_id)
		self.driver.goto(self.select_location.format(location_id))

	def _send_detail(self, detail:dict)->NoReturn:
		"""
		Populate a specific user's detail into the post ad form.
		Elements are matched by 'name' and the 'value' could be the
		input text or input ID depending on element.

		Element types:
		  TEXTAREA = 1
		  TEXT = 2
		  SELECT = 3
		  RADIO = 4
		  CHECKBOX = 5
		  OTHER = 6

		:param detail: {'name':[...], 'value':[...]}
		:return: NoReturn
		"""
		if detail['name'] == 'location':
			change_loc = self.driver.find_element(
				"//button[starts-with(@class,'changeLocationButton')]",
				required=False
			)
			if change_loc is not None:
				change_loc.click()
			self.driver.wait_for_element(
				"//textarea[@id='location']").send_keys(detail['value'])
			try:
				self.driver.wait_for_element(
					"//div[starts-with(@class,'autocompleteSuggestions')]/div[starts-with(@id,'downshift')]"
				).click()
			except:
				pass # do nothing if you can't change the optional address/postal code
			return

		element_type = self._set_detail_type(detail['name'])
		if element_type <= 2: # (1) TEXTAREA and (2) TEXT
			self.driver.send_keys(
				"//{}[@name='{}']".format(
					'input' if element_type == 2 else 'textarea', detail['name']),
				detail['value'])
			# self.driver.send_keys(None, 'TAB')
		elif element_type == 3: # (3) SELECT
			self.driver.select_from_list_by_label(
				"//select[@name='%s']" % detail['name'],
				detail['value']
			)
		elif element_type <= 5: # (4) RADIO and (5) CHECKBOX
			label = self.driver.find_element(
				"//label[@for='%s']" % detail['value'])
			if self.driver.is_visible(label):
				label.click()
			else:
				self.driver.scroll_element_into_view(label)
				sleep(0.5)
				label.click()
		else:
			self.log.critical('Failed to populate a user`s detail. Name: [%s] ,'
			                  'value: [%s].' % (detail['name'], detail['value']))

	def _set_detail_type(self, element_name:str)->int:
		"""Set the element type of a user's detail"""
		# element types
		TEXTAREA = 1
		TEXT = 2
		SELECT = 3
		RADIO = 4
		CHECKBOX = 5
		OTHER = 6

		if self.driver.find_element(
				"//textarea[@name='"+element_name+"']",
				required=False
			) is not None:
			return TEXTAREA
		elif self.driver.find_element(
				"//input[@name='"+element_name+"']",
				required=False
			) is not None:
			type_attribute = self.driver.find_element(
				"//input[@name='"+element_name+"']",
			).get_attribute('type')
			if type_attribute.lower() == 'text':
				return TEXT
			elif type_attribute.lower() == 'radio':
				return RADIO
			elif type_attribute.lower() == 'checkbox':
				return CHECKBOX
			else:
				return OTHER
		elif self.driver.find_element(
				"//select[@name='"+element_name+"']",
				required=False
			) is not None:
			return SELECT
		else:
			return OTHER

	def _sort_my_ads(self):
		""" Sorts ads from oldest to newest. *via expiration date* """
		self.log.info('Sorting ads by expiration date.')
		class_name = self.driver.wait_for_element(
			"//ul[starts-with(@class,'expiresList')]//button/*", # SVG element
		).get_attribute('class')
		while 'isSelected' not in class_name or 'ascending' not in class_name:
			self.driver.click_element(
				"//ul[starts-with(@class,'expiresList')]//button")
			class_name = self.driver.find_element(
				"//ul[starts-with(@class,'expiresList')]//button/*", # SVG element
			).get_attribute('class')
			sleep(1)

	def _submit_post(self, attempts: int=1)->NoReturn:
		"""
		Try to submit form recursively for 4 seconds. Delays can occur after
		selecting a plan making the submit button temporarily unavailable.
		:param attempts: int
		:return: NoReturn
		"""
		if attempts <= 8:
			try:
				btn = self.driver.find_element("//form[starts-with(@id,'PostAd')]")
				if 'shopping' in btn.text.lower():
					raise RuntimeError('Unable to post as only "+ Add to Shopping '
					                   'Cart" is availble (locked in professional '
					                   'mode).')
				btn.submit()
			except:
				sleep(0.5)
				self._submit_post(attempts+1)
		else:
			raise RuntimeError('Failed to submit form after %s attempts.'
			                   % attempts)

	def _upload_images(self, path:str)->NoReturn:
		"""
		Send the absolute path of each file in `path` to kijiji's image field,
		effectively, uploading it.
		:param path: str - absolute path of the images location
		:return: NoReturn
		"""
		self.driver.log.info('Uploading images.')
		files = [os.path.join(path, f) for f in os.listdir(path)
		         if (os.path.isfile(os.path.join(path, f)) and f != '.gitkeep')]
		if len(files) > 0:
			files_string = '\n'.join(files)
			upload_inp = self.driver.find_element('//input[starts-with(@id,"html5")]')
			upload_inp.send_keys(files_string)
			iterations = 1
			while self.driver.find_element('//li[@class="uploading thumbnail"]',
			                      required=False) is None:
				self.driver.log.info('Waiting for `images loading` icon.')
				sleep(0.5)
				iterations = iterations + 1
				if iterations > 20:  # wait up 10 seconds
					self.driver.log.info('Failed to find `images loading` icon.')
					break
			self.driver.wait_for_element('//li[@class="uploading thumbnail"]', negate=True,
			                    timeout=120)
			self.log_alert_message()
		else:
			self.driver.log.info('No images to upload.')