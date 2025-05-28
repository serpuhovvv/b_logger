import pytest
from contextlib import contextmanager

from selenium.webdriver.ie.webdriver import RemoteWebDriver, WebDriver
from playwright.sync_api import Page

from b_logger.entities.steps import StepStatus, Step
from b_logger.entities.exceptions import possible_exceptions
from b_logger.integrations import Integrations
from b_logger.plugin import runtime


class BLogger:

    @staticmethod
    def set_base_url(base_url: str):
        """
        Set base_url for the entire Run
        """
        runtime.set_base_url(base_url)

    @staticmethod
    def set_env(env: str):
        """
        Set env for the entire Run
        """
        runtime.set_env(env)

    @staticmethod
    def set_browser(browser: RemoteWebDriver | WebDriver | Page):
        """
        Set browser in a browser init fixture or in a test

        If browser init fixture name is in
            ["driver", "page", "selenium_driver", "driver_init", "playwright_page"]
        then it will be detected automatically
        """
        runtime.set_browser(browser)

    @staticmethod
    def description(description: str):
        """
        Add Test Description
        Can be used as marker @blog.description()
            as well as function blog.description()
        """
        runtime.apply_description(description)

        return pytest.mark.blog_description(description=description)

    @staticmethod
    def info(*args, **kwargs):
        """
        Leave any info or note about Test Run or Step before or during execution

        Supports:
            - Single String: blog.info('message')
            - Key-Value: blog.info(first_parameter='param 1', second_parameter='param 2')
            - Tuple: blog.info("Name", "Value")
        """
        runtime.apply_info(*args, **kwargs)

        return pytest.mark.blog_info(args=args, kwargs=kwargs)

    @staticmethod
    def known_bug(description: str, url: str = None):
        """
        Mark the test as having a known bug or apply it to current step.

        :param description: Short explanation of the bug.
        :param url: Link to bug tracker or documentation.
        """
        runtime.apply_known_bug(description, url)

        return pytest.mark.blog_known_bug(description=description, url=url)

    @staticmethod
    @contextmanager
    def step(title: str, expected: str = None):
        with Integrations.steps(title, expected):

            step = Step(title=title, expected=expected)

            runtime.start_step(step)

            try:
                yield
                runtime.handle_step_result(step)

            except possible_exceptions as e:
                runtime.handle_step_result(step, e)
                raise e

            finally:
                runtime.finish_step(step)

    @staticmethod
    def print(message: str, status: StepStatus = StepStatus.NONE):
        """
        Print any message
            It will be added to a Current Step
        """
        runtime.print_message(message, status)

    @staticmethod
    def attach(source, name: str = None):
        """
        Attach file or screenshot
            It will be added to Test Run and Current Step
        """
        runtime.attach(source, name)

    @staticmethod
    def screenshot(name: str = None, is_error: bool = False):
        """
        Make screenshot
            It will be automatically attached to Test Run and Current Step
            Will do nothing if no browser is used
        """
        runtime.make_screenshot(name, is_error)
