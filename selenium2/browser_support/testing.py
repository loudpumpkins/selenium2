import json
import os
from difflib import unified_diff
from bs4 import BeautifulSoup

from ..logger import Logger
from .screenshot import Screenshot


class Testing(Screenshot):
    """
    Class for automated visual regression testing.

    This class is designed to extend the selenium2 wrapper to help with visual
    regression testing. The `check_window` method allows for comparing the
    current state of a web page to a previously saved baseline and identifying
    layout differences based on HTML structure.
    """

    def __init__(self, root):
        super().__init__(root)
        self.log = Logger.get_logger()

    def verify_visual_baseline(self, level=1, baseline=False, name=None):
        """
        Compares the current window's HTML structure to a visual baseline or sets
        a new baseline.

        Args:
            level (int, optional): Comparison strictness lvl (1, 2, or 3).
                Defaults to 1.
            baseline (bool, optional): If True, sets a new baseline for the window.
                Defaults to False.
            name (str, optional): Optional name to uniquely identify the baseline.
                Defaults to None.
        """
        try:
            level = int(level)
            if level < 1 or level > 3:
                raise ValueError
        except ValueError:
            raise ValueError('Parameter "level" must be set to 1, 2, or 3!')

        # Determine test and path names
        test_path, test_name = self._get_test_info(name)

        # Define baseline paths
        visual_baseline_path = os.path.join(self._root.report_directory, test_path, test_name).__str__()
        baseline_png = "baseline.png"
        baseline_png_path = os.path.join(visual_baseline_path, baseline_png)
        latest_png = "latest.png"
        level_files = {
            1: os.path.join(visual_baseline_path, "tags_level_1.txt"),
            2: os.path.join(visual_baseline_path, "tags_level_2.txt"),
            3: os.path.join(visual_baseline_path, "tags_level_3.txt")
        }

        # Determine whether to set a new baseline
        set_baseline = baseline or not self._baseline_exists(
            visual_baseline_path, baseline_png_path, level_files
        )

        # Retrieve HTML tags and attributes
        soup = self._get_beautiful_soup()
        html_tags = soup.body.find_all()
        levels_data = {
            1: json.dumps([[tag.name] for tag in html_tags], indent=2),
            2: json.dumps([[tag.name, sorted(tag.attrs.keys())] for tag in html_tags], indent=2),
            3: json.dumps([[tag.name, sorted(tag.attrs.items())] for tag in html_tags], indent=2),
        }

        # Set the screenshot directory
        self.set_screenshot_directory(visual_baseline_path, append=False)

        if set_baseline:
            # Save baseline data
            self.capture_page_screenshot(baseline_png)
            for lvl, file_path in level_files.items():
                with open(file_path, 'w', encoding='utf-8') as fd:
                    fd.writelines(levels_data[lvl])
        else:
            # Compare against existing baseline
            baseline_data = {}
            self.capture_page_screenshot(latest_png)
            for lvl, file_path in level_files.items():
                with open(file_path, 'r', encoding='utf-8') as fd:
                    baseline_data[lvl] = fd.read()

            # Perform comparison
            baseline = baseline_data[level]
            current = levels_data[level]
            if baseline != current:
                diff = "".join(
                    unified_diff(
                        baseline.splitlines(keepends=True), current.splitlines(keepends=True),
                        fromfile='baseline', tofile='current', lineterm='', n=3
                    )
                )
                self._fail(f"Level ({level}) visual layout regression test failed.\n"
                           f"Differences:\n{diff}")

    def set_report_directory(self, path=None, append=True):
        """
        Sets the directory for reports.

        ``path`` can be an absolute path or relative path from the current
        report_directory. If the directory does not exist, it will be
        created.

        ``append`` is set to True by default and will append to current path and
        normalise it, where False will overwrite the path attribute.

        Will return the previous path to be stored and re-set if needed.

        :param path: str - the path to append or set
        :param append: bool - True will add / False will replace
        :return: str - previous path
        """
        if path is not None:
            path = os.path.normpath(os.path.join(self._root.report_directory, path)) \
                if append else path
            self._create_directory(path)
        previous = self._root.report_directory
        path = os.path.abspath(path)
        self.log.info('Setting report directory from {} to {}'.format(
            previous, path
        ))
        self._root.report_directory = path
        return previous

    def _baseline_exists(self, visual_baseline_path, baseline_png_path, level_files):
        """
        Checks if a baseline exists by verifying the presence of required files.

        Args:
            visual_baseline_path (str): Path to the baseline directory.
            baseline_png_path (str): Path to the baseline image.
            level_files (dict): Dictionary containing paths to the lvl files.

        Returns:
            bool: True if the baseline exists, False otherwise.
        """
        if not os.path.exists(visual_baseline_path):
            os.makedirs(visual_baseline_path)
            return False
        if not os.path.exists(baseline_png_path):
            return False
        for file in level_files.values():
            if not os.path.exists(file):
                return False
        return True

    def _fail(self, error_message):
        """
        Raises an error using pytest's fail function if available; otherwise, raises
        an AssertionError.

        Args:
            error_message (str): The error message to display.
        """
        # Attempt to import pytest for cleaner error handling
        try:
            import pytest
        except ImportError:
            pytest = None

        if pytest:
            pytest.fail(error_message, pytrace=False)
        else:
            raise AssertionError(error_message)

    def _get_beautiful_soup(self):
        """
        Retrieves the BeautifulSoup object of the current page.

        Returns:
            BeautifulSoup: Parsed BeautifulSoup object.
        """
        source = self.driver.page_source
        return BeautifulSoup(source, "html.parser")

    def _get_test_info(self, name=None):
        """
        Retrieves the test path and name from the environment or uses defaults.

        Args:
            name (str, optional): Optional custom test name. Defaults to None.

        Returns:
            tuple: A tuple containing test path and test name.
        """
        if os.environ.get("PYTEST_CURRENT_TEST"):
            test_path, test_name = os.environ["PYTEST_CURRENT_TEST"].split("::")[:2]
            test_path = test_path.replace('/', ".").replace('.py', '')
            test_name = test_name.split(" ")[0]
        else:
            test_path, test_name = '', 'default'
        if name:
            test_name = name
        return test_path, test_name
