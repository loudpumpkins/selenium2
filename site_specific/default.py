from typing import NoReturn

from ..logger import Logger


class DefaultBehaviour:
    """
    Default SITE behaviour such as login, logout, etc. to be implemented by all
    site-specific classes.
    """
    name = 'default'

    def __init__(self, driver):
        self.driver = driver
        self.log = Logger().log

    def create_account(self, details: dict, cookies: str = None) -> bool:
        """
        Create an account for the site using the credentials found in `details`.
        If a `cookies` filename is provided, it will save the cookies after creating
        an account.

        :return: bool - True for success
        """
        self._not_implementated('create_account')

    def create_content(self, details: dict) -> str:
        """
        Post an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: str - returns an identifier to the new content (url, ID, ...)
        """
        self._not_implementated('create_content')

    def delete_content(self, details: dict) -> bool:
        """
        Delete an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: bool - returns True if content found and delete. False otherwise.
        """
        self._not_implementated('delete_content')

    def edit_content(self, details: dict) -> bool:
        """
        Edit an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: bool - returns True of content found and edited. False otherwise.
        """
        self._not_implementated('edit_content')

    def is_signed_in(self) -> bool:
        """
        Explicitly assert that user is logged in. Does not rely on 'is_signed_out'.

        :return: bool - True for logged in
        """
        self._not_implementated('is_signed_in')

    def is_signed_out(self) -> bool:
        """
        Explicitly assert that user is logged out. Does not rely on 'is_signed_in'.

        :return: bool - True for logged out
        """
        self._not_implementated('is_signed_out')

    def sign_in(self, details: dict, cookies: str = None) -> NoReturn:
        """
        Sign in to the site using the credentials found in `details`.
        If a `cookies` filename is provided, it will try to load it and see if
        the user is now logged in.
        If the `cookies` filename is not found, it will try to sign in normally
        and save the `cookies` file after signing in.
        """
        self._not_implementated('sign_in')

    def sign_out(self) -> NoReturn:
        """
        Sign out from the site. Will try assert that sign_out() was successful.
        """
        self._not_implementated('sign_out')

    def _not_implementated(self, method):
        raise NotImplemented('Method `%s` is not implemented or site specific '
                             'behaviour was not set.\nSet a site specific behaviour '
                             'using `Browser.set_site_behaviour(site_name)`.' % method)