import os

# general purpose
DEBUG = True

# default timeout in seconds for explicit waits as an int
DEFAULT_TIMEOUT = 2

# default location to store screenshots. Can be changed using set_screenshot_directory(path)
SCREENSHOT_ROOT_DIRECTORY = os.path.abspath(
	os.path.join(

		# file directory (.../selenium/config)
		os.path.dirname(os.path.abspath(__file__)),

		# parent node (.../selenium)
		os.pardir,

		# sibling node (../selenium/screenshots)
		'screenshots'
	)
)

print(SCREENSHOT_ROOT_DIRECTORY)

# running speed of the script
DEFAULT_SPEED = 0.0