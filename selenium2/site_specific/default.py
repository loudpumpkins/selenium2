from typing import NoReturn, Protocol

from ..logger import Logger


class SiteBehaviour(Protocol):
    """
    Protocol defining site-specific behaviour such as login, logout, etc.,
    that must be implemented by all site-specific classes.
    """
    def __init__(self, browser):
        self.browser = browser

    def create_account(self, details: dict, cookies: str = None) -> bool:
        """
        Create an account for the site using the credentials found in `details`.
        If a `cookies` filename is provided, it will save the cookies after creating
        an account.

        :return: bool - True for success
        """
        ...

    def create_content(self, details: dict) -> str:
        """
        Post an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: str - returns an identifier to the new content (url, ID, ...)
        """
        ...

    def delete_content(self, details: dict) -> bool:
        """
        Delete an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: bool - returns True if content found and delete. False otherwise.
        """
        ...

    def edit_content(self, details: dict) -> bool:
        """
        Edit an ad, a tweet, a post, an image, etc. The main purpose of the
        site that we are building behaviour for.

        :return: bool - returns True of content found and edited. False otherwise.
        """
        ...

    def is_signed_in(self) -> bool:
        """
        Explicitly assert that user is logged in. Does not rely on 'is_signed_out'.

        :return: bool - True for logged in
        """
        ...

    def is_signed_out(self) -> bool:
        """
        Explicitly assert that user is logged out. Does not rely on 'is_signed_in'.

        :return: bool - True for logged out
        """
        ...

    def sign_in(self, details: dict, cookies: str = None) -> NoReturn:
        """
        Sign in to the site using the credentials found in `details`.
        If a `cookies` filename is provided, it will try to load it and see if
        the user is now logged in.
        If the `cookies` filename is not found, it will try to sign in normally
        and save the `cookies` file after signing in.
        """
        ...

    def sign_out(self) -> NoReturn:
        """
        Sign out from the site. Will try assert that sign_out() was successful.
        """
        ...
