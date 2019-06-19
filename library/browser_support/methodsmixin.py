from config import *

# external

# internal
from ..logger import Logger
from .base import Base


class MethodsMixin(Base):

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def test(self):
		print("im a test from methodsmixin")