from ..config import *

# external
from selenium.webdriver.support.ui import Select

# internal
from ..logger import Logger
from ._base import Base


class Selects(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def get_select_items(self, locator, values=False):
		"""
		Returns all labels or values of a <select> Tag identified by ``locator``.

		Will return labels by default, but can return values if ``values`` is
		set to true.

		Example:
		<select id="myId">
            <option value="books">Books</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
            <option value="php">PHP</option>
            <option value="js">JavaScript</option>
        </select>

        get_select_items('#myId', values=False)
            returns: ['Books', 'HTML', 'CSS', 'PHP', 'JavaScript']

        get_select_items('#myId', values=True)
            returns: ['books', 'html', 'css', 'php', 'js']

        See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param values: bool - True returns values / False returns labels
		:return: List[str]
		"""
		options = self._get_options(locator)
		self.log.info('Getting a list of all {} in {} <select> tag.'.format(
			'VALUES' if values else 'LABELS', locator
		))
		if values:
			return self._get_values(options)
		else:
			return self._get_labels(options)

	def get_selected_item(self, locator, values=False):
		"""
		Returns the label or value of a <select> Tag identified by ``locator``.

		If there are multiple selected options, label of the first option
		is returned.

		Will return the label by default; set ``values`` to True to get the value.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param values: bool - True returns values / False returns labels
		:return: str
		"""
		select = self._get_select_list(locator)
		self.log.info('Getting the selected {} in {} <select> tag.'.format(
			'VALUE' if values else 'LABEL', locator
		))
		if values:
			return select.first_selected_option.get_attribute('value')
		else:
			return select.first_selected_option.text

	def select_all_from_multilist(self, locator):
		"""
		Selects all options from multi-selection list ``locator``.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info("Selecting all options from list '%s'." % locator)
		select = self._get_select_list(locator)
		if not select.is_multiple:
			raise RuntimeError("'Select All From List' works only with "
			                   "multi-selection lists.")
		for i in range(len(select.options)):
			select.select_by_index(i)

	def select_from_list_by_index(self, locator, *indexes):
		"""
		Selects options from selection list ``locator`` by ``indexes``.

		Indexes of list options start from 0 and must be provided as strings

		If more than one option is given for a single-selection list,
		the last value will be selected. With multi-selection lists all
		specified options are selected, but possible old selections are
		not cleared.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param indexes: *str
		:return: NoReturn
		"""
		if not indexes:
			raise ValueError("No indexes given.")
		self.log.info("Selecting options from selection list '%s' by index%s %s."
		          % (locator, '' if len(indexes) == 1 else 'es',
		             ', '.join(indexes)))
		select = self._get_select_list(locator)
		for index in indexes:
			select.select_by_index(int(index))

	def select_from_list_by_value(self, locator, *values):
		"""
		Selects options from selection list ``locator`` by ``values``.

		If more than one option is given for a single-selection list,
		the last value will be selected. With multi-selection lists all
		specified options are selected, but possible old selections are
		not cleared.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param values: *str
		:return: NoReturn
		"""
		if not values:
			raise ValueError("No values given.")
		self.log.info("Selecting options from selection list '%s' by value(s) %s."
		          % (locator, ', '.join(values)))
		select = self._get_select_list(locator)
		for value in values:
			select.select_by_value(value)

	def select_from_list_by_label(self, locator, *labels):
		"""
		Selects options from selection list ``locator`` by ``labels``.

		If more than one option is given for a single-selection list,
		the last value will be selected. With multi-selection lists all
		specified options are selected, but possible old selections are
		not cleared.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param labels: *str
		:return: NoReturn
		"""
		if not labels:
			raise ValueError("No labels given.")
		self.log.info("Selecting options from selection list '%s' by label(s) %s."
		          % (locator, ', '.join(labels)))
		select = self._get_select_list(locator)
		for label in labels:
			select.select_by_visible_text(label)

	def unselect_all_from_list(self, locator):
		"""
		Unselects all options from multi-selection list ``locator``.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:return: NoReturn
		"""
		self.log.info("Unselecting all options from list '%s'." % locator)
		select = self._get_select_list(locator)
		if not select.is_multiple:
			raise RuntimeError("Un-selecting options works only with "
			                   "multi-selection lists.")
		select.deselect_all()

	def unselect_from_list_by_index(self, locator, *indexes):
		"""
		Unselects options from selection list ``locator`` by ``indexes``.
		Indexes of list options start from 0. This function works only with
		multi-selection lists.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param indexes: *str
		:return: NoReturn
		"""
		if not indexes:
			raise ValueError("No indexes given.")
		self.log.info("Un-selecting options from selection list '%s' by index%s "
		          "%s." % (locator, '' if len(indexes) == 1 else 'es',
		                   ', '.join(indexes)))
		select = self._get_select_list(locator)
		if not select.is_multiple:
			raise RuntimeError("Un-selecting options works only with "
			                   "multi-selection lists.")
		for index in indexes:
			select.deselect_by_index(int(index))

	def unselect_from_list_by_value(self, locator, *values):
		"""
		Unselects options from selection list ``locator`` by ``values``.
		This function works only with multi-selection lists.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param values: *str
		:return: NoReturn
		"""
		if not values:
			raise ValueError("No values given.")
		self.log.info("Un-selecting options from selection list '%s' by value(s) "
		          "%s." % (locator, ', '.join(values)))
		select = self._get_select_list(locator)
		if not select.is_multiple:
			raise RuntimeError("Un-selecting options works only with "
			                   "multi-selection lists.")
		for value in values:
			select.deselect_by_value(value)

	def unselect_from_list_by_label(self, locator, *labels):
		"""
		Unselects options from selection list ``locator`` by ``labels``.
		This function works only with multi-selection lists.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str
		:param labels: *str
		:return: NoReturn
		"""
		if not labels:
			raise ValueError("No labels given.")
		self.log.info("Un-selecting options from selection list '%s' by label(s) "
		          "%s." % (locator, ', '.join(labels)))
		select = self._get_select_list(locator)
		if not select.is_multiple:
			raise RuntimeError("Un-selecting options works only with "
			                   "multi-selection lists.")
		for label in labels:
			select.deselect_by_visible_text(label)

	def _get_labels(self, options):
		return [opt.text for opt in options]

	def _get_options(self, locator):
		return self._get_select_list(locator).options

	def _get_values(self, options):
		return [opt.get_attribute('value') for opt in options]

	def _get_selected_options(self, locator):
		return self._get_select_list(locator).all_selected_options

	def _get_select_list(self, locator):
		el = self.find_element(locator, tag='list')
		return Select(el)

