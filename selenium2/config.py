import os

# general purpose
DEBUG = os.environ.get('SELENIUM2_DEBUG', False)

# default timeout in seconds for explicit waits as an int
DEFAULT_TIMEOUT = os.environ.get('SELENIUM2_DEFAULT_TIMEOUT', 15)

SCREENSHOT_ROOT_DIRECTORY = os.environ.get('SELENIUM2_SCREENSHOT_PATH', 'screenshots')
COOKIES_ROOT_DIRECTORY = os.environ.get('SELENIUM2_COOKIES_PATH', 'cookies')

# running speed of the script
DEFAULT_SPEED = os.environ.get('DEFAULT_SPEED', 0.0)