from ..config import *

# external
import os
from collections import namedtuple
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support.wait import WebDriverWait

# internal
from ..logger import Logger
from ._driver import Driver


class Javascript(Driver):

	js_marker = 'JAVASCRIPT'
	arg_marker = 'ARGUMENTS'

	def __init__(self, root):
		super().__init__(root)
		self.log = Logger().log

	def execute_javascript(self, *code):
		"""
		Executes the given JavaScript code with possible arguments.

		``code`` may be divided into multiple arguments in the test data and
		``code`` may contain multiple lines of code and arguments. In that case,
		the JavaScript code parts are concatenated together without adding
		spaces and optional arguments are separated from ``code``.

		If ``code`` is a path to an existing file, the JavaScript
		to execute will be read from that file.

		The JavaScript executes in the context of the currently selected
		frame or window as the body of an anonymous function. Use ``window``
		to refer to the window of your application and ``document`` to refer
		to the document object of the current frame or window, e.g.
		``document.getElementById('example')``.

		This function returns whatever the executed JavaScript code returns.
		Return values are converted to the appropriate Python types.

		Usage:
		execute_javascript("window.myFunc('arg1', 'arg2')")
		execute_javascript('path/js_file.js')
		execute_javascript('alert(arguments[0]);', 'ARGUMENTS', '123')
		execute_javascript('ARGUMENTS', '123', 'JAVASCRIPT', 'alert(arguments[0]);')

		:param code: List[str]
		:return: Any - whatever the executed JavaScript code returns
		"""
		js_code, js_args = self._get_javascript_to_execute(code)
		self._js_logger('Executing JavaScript', js_code, js_args)
		return self.driver.execute_script(js_code, *js_args)

	def inject_jQuery(self):
		"""
		Will inject jQuery version 3.4.1 into the current page if it is not
		already available.

		:return: NoReturn
		"""
		try:
			version = self.driver.execute_script(
				'return window.jQuery.prototype.jquery')
		except JavascriptException:
			self.log.info('Injecting jQuery into page.')
			js_code = """
				var jquery = document.createElement('script');
				jquery.type = 'text/javascript';
				jquery.src = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js';
				document.getElementsByTagName('head')[0].append(jquery);
				"""
			self.driver.execute_script(js_code)
			wait = WebDriverWait(driver=self.driver, timeout=DEFAULT_TIMEOUT,
			                     ignored_exceptions=JavascriptException)
			wait.until(lambda driver: True if driver.execute_script(
					'return window.jQuery.prototype.jquery') else False)
		else:
			self.log.info('jQuery version {} already available for use.'.format(
				version))


	######################################################
	### Snippets below from Robot Framework Foundation ###
	######################################################

	def execute_async_javascript(self, *code):
		"""Executes asynchronous JavaScript code with possible arguments.

		Similar to `Execute Javascript` except that scripts executed with
		this keyword must explicitly signal they are finished by invoking the
		provided callback. This callback is always injected into the executed
		function as the last argument.

		Scripts must complete within the script timeout or this keyword will
		fail. See the `Timeout` section for more information.

		Starting from SeleniumLibrary 3.2 it is possible to provide JavaScript
		[https://seleniumhq.github.io/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html#selenium.webdriver.remote.webdriver.WebDriver.execute_async_script|
		arguments] as part of ``code`` argument. See `Execute Javascript` for
		more details.

		Examples:
		| `Execute Async JavaScript` | var callback = arguments[arguments.length - 1]; window.setTimeout(callback, 2000); |
		| `Execute Async JavaScript` | ${CURDIR}/async_js_to_execute.js |
		| ${result} = | `Execute Async JavaScript`                      |
		| ...         | var callback = arguments[arguments.length - 1]; |
		| ...         | function answer(){callback("text");};           |
		| ...         | window.setTimeout(answer, 2000);                |
		| `Should Be Equal` | ${result} | text |
		"""
		js_code, js_args = self._get_javascript_to_execute(code)
		self._js_logger('Executing Asynchronous JavaScript', js_code, js_args)
		return self.driver.execute_async_script(js_code, *js_args)

	def _js_logger(self, base, code, args):
		message = '{}:\n{}\n'.format(base, code)
		if args:
			message = ('{}By using argument(s):\n{}'.format(message, args))
		else:
			message = '%sWithout any arguments.' % message
		self.log.info(message)

	def _get_javascript_to_execute(self, code):
		js_code, js_args = self._separate_code_and_args(code)
		if not js_code:
			raise ValueError(
				'JavaScript code was not found from code argument.')
		js_code = ''.join(js_code)
		path = js_code.replace('/', os.sep)
		if os.path.isfile(path):
			js_code = self._read_javascript_from_file(path)
		return js_code, js_args

	def _separate_code_and_args(self, code):
		code = list(code)
		self._check_marker_error(code)
		index = self._get_marker_index(code)
		if self.arg_marker not in code:
			return code[index.js + 1:], []
		if self.js_marker not in code:
			return code[0:index.arg], code[index.arg + 1:]
		else:
			if index.js == 0:
				return code[index.js + 1:index.arg], code[index.arg + 1:]
			else:
				return code[index.js + 1:], code[index.arg + 1:index.js]

	def _check_marker_error(self, code):
		if not code:
			raise ValueError('There must be at least one argument defined.')
		message = None
		template = '%s marker was found two times in the code.'
		if code.count(self.js_marker) > 1:
			message = template % self.js_marker
		if code.count(self.arg_marker) > 1:
			message = template % self.arg_marker
		index = self._get_marker_index(code)
		if index.js > 0 and index.arg != 0:
			message = template % self.js_marker
		if message:
			raise ValueError(message)

	def _get_marker_index(self, code):
		Index = namedtuple('Index', 'js arg')
		if self.js_marker in code:
			js = code.index(self.js_marker)
		else:
			js = -1
		if self.arg_marker in code:
			arg = code.index(self.arg_marker)
		else:
			arg = -1
		return Index(js=js, arg=arg)

	def _read_javascript_from_file(self, path):
		self.log.info('Reading JavaScript from file <a href="file://%s">%s</a>.'
		          % (path.replace(os.sep, '/'), path))
		with open(path) as file:
			return file.read().strip()

	######################################################
	### END of snippet from Robot Framework Foundation ###
	######################################################