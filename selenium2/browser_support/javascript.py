import os

from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support.wait import WebDriverWait

from ..config import *
from ..logger import Logger
from ._driver import Driver


class Javascript(Driver):

    def __init__(self, root):
        super().__init__(root)
        self.log = Logger.get_logger()

    def execute_javascript(self, script, *args):
        """
        Executes the given JavaScript code with possible arguments in the context
        of the currently selected frame or window (document.getElement or window.alert).

        If the `script` parameter is a path to an existing file, the JavaScript
        code to be executed will be read from that file. If `script` contains
        JavaScript code directly, it will execute as it is. Multiple arguments can
        be passed and will be available in the executed JavaScript environment as
        `arguments[0]`, `arguments[1]`, etc.

        Args:
            script (str): The JavaScript code to execute or a path to a JavaScript file.
            *args (str): Optional arguments that can be accessed in the JavaScript via
                         `arguments` array.

        Returns:
            The result of the executed JavaScript code, with return values converted
            to the appropriate Python types.

        Usage Examples:
            # Direct code execution
            execute_javascript("window.func('arg1', 'arg2')")

            # Executing JavaScript from a file
            execute_javascript('/path/to/file.js')

            # Executing JavaScript with arguments
            execute_javascript('alert(arguments[0], arguments[1]);', '123', '456')

        """
        if self._is_file(script):
            script = self._read_file(script)
        self.log.info(f'Executing JavaScript: "{script}" with arguments: "{args}"')
        return self.driver.execute_script(script, *args)

    def execute_async_javascript(self, script, *args):
        """
        Asynchronously executes JavaScript in the context of the currently selected
        frame or window. This function is useful for dealing with JavaScript that
        performs asynchronous operations such as timeouts, intervals, AJAX requests,
        or any operations which require a callback.

        The `script` should include a mechanism to signal completion, typically by
        accepting a callback function as the last argument and calling it upon completion.
        The arguments provided in `*args` are passed to the JavaScript script as
        `arguments[0]`, `arguments[1]`, etc., up to `arguments[n-1]`, where `n` is
        the total number of arguments. The last argument (`arguments[n]`) is reserved
        for the callback function that Selenium injects to signal completion.

        Args:
            script (str): The JavaScript code to execute. It should include a
                          callback to signal completion.
            *args: Variable length argument list for your JavaScript, excluding
                          the callback.

        Returns:
            The result returned by the JavaScript through the callback, with the value
            converted to the appropriate Python type.

        Usage:
            # Example script that uses a timeout to simulate async behavior
            script = "var callback = arguments[arguments.length - 1]; " \\
                     "window.setTimeout(function(){ callback('timeout') }, 3000);"
            result = driver.execute_async_script(script)
            print(result)  # This will print 'timeout' after 3 seconds

            # Example handling Promises
            data = "Promise resolved with external data"
            script = '''
            var callback = arguments[arguments.length - 1];
            new Promise((resolve, reject) => {
                resolve(arguments[0]);
            })
            .then(response => callback(response));
            '''
            result = driver.execute_async_script(script, data)
            print(result)  # Outputs "Promise resolved with external data"

            # Example handling AJAX requests
            url = "https://api.example.com/data"
            script = '''
            var callback = arguments[arguments.length - 1];
            var xhr = new XMLHttpRequest();
            xhr.open('GET', arguments[0], true);
            xhr.onreadystatechange = function() {
              if (xhr.readyState == 4 && xhr.status == 200) {
                callback(xhr.responseText);
              }
            };
            xhr.send();
            '''
            result = driver.execute_async_script(script, url)
            print(result)  # Outputs the response text from the API call.
        """
        if self._is_file(script):
            script = self._read_file(script)
        self.log.info(f'Executing Asynchronous JavaScript: "{script}" with '
                      f'arguments: "{args}"')
        return self.driver.execute_async_script(script, *args)

    def _is_file(self, path):
        path = path.replace('/', os.sep)
        return os.path.isfile(path)

    def _read_file(self, path):
        self.log.info(f'Reading JavaScript from file {path}.')
        with open(path) as file:
            return file.read().strip()
