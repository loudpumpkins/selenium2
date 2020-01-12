import os

# general purpose
DEBUG = True

# default timeout in seconds for explicit waits as an int
DEFAULT_TIMEOUT = 15

# default location to store screenshots. Can be changed using set_screenshot_directory(path)
SCREENSHOT_ROOT_DIRECTORY = os.path.abspath(
	os.path.join(

		# file directory (.../selenium2/config)
		os.path.dirname(os.path.abspath(__file__)),

		# parent node (.../selenium2)
		os.pardir,

		# sibling node (../selenium2/screenshots)
		'screenshots'
	)
)

# running speed of the script
DEFAULT_SPEED = 0.0