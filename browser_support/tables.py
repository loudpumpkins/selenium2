from ..config import *

# external

# internal
from ..logger import Logger
from ._base import Base


class Tables(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def get_table_cell_by_index(self, locator, row, column):
		"""
		Returns the cell WebElement identified by ``row`` and ``column``
		within the table identified by ``locator``

		Both row and column indexes start from 1. It is possible to refer to
		rows and columns from the end by using negative indexes so that -1
		is the last row/column, -2 is the second last, and so on.

		This function will have unexpected results if the table identified by
		``locator``	has nested tables as all the <th>, <td> and <tr> tags
		are added to the list of elements regardless of who is the immediate
		parent of the node.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str - the table
		:param row: str or int - first index starts at 1
		:param column: str or int - first index starts at 1
		:return: WebElement or IndexError exception
		"""
		row = int(row) - 1 if int(row) > 0 else int(row)
		column = int(column) - 1 if int(column) > 0 else int(column)
		table = self.find_element(locator, tag='table')
		row = self._get_row(table, row)
		cell = self._get_cell(row, column)
		return cell

	def get_table_cell_text(self, locator, row, column):
		"""
		Returns the cell's text identified by ``row`` and ``column``
		within the table identified by ``locator``

		Both row and column indexes start from 1. It is possible to refer to
		rows and columns from the end by using negative indexes so that -1
		is the last row/column, -2 is the second last, and so on.

		This function will have unexpected results if the table identified by
		``locator``	has nested tables as all the <th>, <td> and <tr> tags
		are added to the list of elements regardless of who is the immediate
		parent of the node.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str - the table
		:param row: str or int - first index starts at 1
		:param column: str or int - first index starts at 1
		:return: text or IndexError exception
		"""
		return self.get_table_cell_by_index(locator, row, column).text

	def get_table_cell_by_text(self, locator, text):
		"""
		Returns the cell WebElement that's content is equal to the ``text``
		provided within the table identified by ``locator``

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str - the table
		:param text: str
		:return: WebElement or IndexError exception
		"""
		row = self.get_table_row_by_text(locator, text)
		if row is not None:
			return self._get_cell_with_text(row, text)
		return None

	def get_table_row_by_index(self, locator, row):
		"""
		Returns a list of cell WebElements identified by ``row`` number in
		the table identified by ``locator``

		Row indexes start from 1. It is possible to refer to rows from the end
		by using negative indexes so that -1 is the last row, -2 is the second
		last, and so on.

		This function will have unexpected results if the table identified by
		``locator``	has nested tables as all the <th>, <td> and <tr> tags
		are added to the list of elements regardless of who is the immediate
		parent of the node.

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str - the table
		:param row: str or int - first index starts at 1
		:return: List[WebElements] or []
		"""
		row = int(row) - 1 if int(row) > 0 else int(row)
		table = self.find_element(locator, tag='table')
		row_element = self._get_row(table, row)
		return self.find_elements('.//th|.//td', parent=row_element)

	def get_table_row_by_text(self, locator, text):
		"""
		Returns a list of all cell WebElements of a row which contains a cell
		with text equal to ``text`` in the table identified by ``locator``

		See `find_element` method in `_base.py` for ``locator`` usage/syntax

		:param locator: WebElement or str - the table
		:param text: str
		:return: List[WebElements] or []
		"""
		table = self.find_element(locator, tag='table')
		rows = self.find_elements('.//tr', parent=table)
		for row in rows:
			if self._get_cell_with_text(row, text) is not None:
				return self.find_elements('.//th|.//td', parent=row)
		return []

	def _get_row(self, table, row_index):
		rows = self.find_elements('.//tr', parent=table)
		try:
			row = rows[row_index]
		except IndexError:
			raise IndexError("Failed to find the row as the index is out of "
			                 "bound. The table has {} rows".format(len(rows)))
		return row

	def _get_cell(self, row, column_index):
		cells = self.find_elements('.//th|.//td', parent=row)
		try:
			cell = cells[column_index]
		except IndexError:
			raise IndexError("Failed to find the cell as the index is out of "
			                 "bound. The row has {} cells.".format(len(cells)))
		return cell

	def _get_cell_with_text(self, row, text):
		cells = self.find_elements('.//th|.//td', parent=row)
		for cell in cells:
			if cell.text == text:
				return cell
		return None