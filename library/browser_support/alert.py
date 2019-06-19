from config import *

# external

# internal
from ..logger import Logger
from .base import Base


class Alert(Base):
	ACCEPT = 'ACCEPT'
	DISMISS = 'DISMISS'
	LEAVE = 'LEAVE'
	_next_alert_action = ACCEPT

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def test(self):
		print("im a test from methodsmixin")