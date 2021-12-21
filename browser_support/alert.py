from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.webdriver.support.ui import WebDriverWait

from ..config import *
from ..logger import Logger
from ._driver import Driver


class Alert(Driver):
    _next_alert_action = 'accept'

    def __init__(self, root):
        super().__init__(root)
        self.log = Logger().log

    def get_alert(self, timeout=DEFAULT_TIMEOUT,
                  message='Getting alert with a timeout of {} second(s).'):
        """
        Switch focus to the alert and return it.
        get_alert() will place the timeout in seconds into the ``message`` if
        an extra set of curly brackets {} are placed.

        :param timeout: int - time in seconds for explicit wait
        :param message: str - error message to return in case of failure
        :return: alert selenium.webdriver.common.alert import Alert
        """
        self.log.info(message.format(timeout))
        try:
            alert = WebDriverWait(self.driver, timeout).until(alert_is_present())
            return alert
        except TimeoutException as error:
            error.msg = (f'Failed to find the alert before the timeout '
                         f' [{timeout} second(s)].')
            raise NoAlertPresentException('Failed to find an alert') from error

    def get_alert_text(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the text value in the alert

        :param timeout:
        :return:
        """
        alert = self.get_alert(timeout,
                               message='Getting alert text with a timeout of {} second(s).')
        return self._handle_alert(alert, 'ignore')

    def handle_alert(self, action='accept', timeout=DEFAULT_TIMEOUT):
        """
        Handles an alert and returns it's text as a string

        Allowed actions:
        `ACCEPT` - (DEFAULT) - Will accept or press 'OK'
        `DISMISS` - Will dismiss the alert by pressing 'CANCEL' or 'CLOSE'
        `IGNORE` - Will ignore the alert and do nothing

        :param action: str - case insensitive
        :param timeout: int - time in seconds for explicit wait
        :return: str - the text value of the alert
        """
        log_message = ('Handling alert [action:%s] with a timeout of {} seconds' % action.lower())
        alert = self.get_alert(timeout, message=log_message)
        return self._handle_alert(alert, action)

    def input_text_into_alert(self, text, action='accept', timeout=DEFAULT_TIMEOUT):
        """
        Types the given ``text`` into an input field in an alert.
        :param text: str - the text to type into the prompt
        :param action: str - ACCEPT/DISMISS/IGNORE
        :param timeout: int - explicit wait time in seconds
        :return: str - the text of the prompt
        """
        log_message = ('Placing text [%s] into alert [action:%s] with a timeout '
                       'of {} seconds' % (text, action.lower()))
        alert = self.get_alert(timeout, message=log_message)
        alert.send_keys(text)
        self._handle_alert(alert, action)

    def _handle_alert(self, alert, action):
        """
        See handle_alert() for details
        :param alert: selenium.webdriver.common.alert import Alert
        :param action: str - accept / dismiss / leave
        :return: str - the text value of the alert
        """
        actn = action.upper()
        text = ' '.join(alert.text.splitlines())
        if actn == 'ACCEPT' or actn == 'OK' or actn == 'ACK':
            alert.accept()
        elif actn == 'CANCEL' or actn == 'DISMISS' or actn == 'CLOSE':
            alert.dismiss()
        elif not (actn == 'IGNORE' or actn == 'NONE' or actn == 'LEAVE'):
            raise ValueError('Invalid alert action: {}.'.format(action))
        return text

