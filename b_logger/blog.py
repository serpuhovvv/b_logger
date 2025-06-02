import pytest
from contextlib import contextmanager

from selenium.webdriver.ie.webdriver import RemoteWebDriver, WebDriver
from playwright.sync_api import Page

from b_logger.entities.prints import PrintStatus
from b_logger.entities.steps import Step
from b_logger.entities.exceptions import possible_exceptions
from b_logger.integrations import Integrations
from b_logger.plugin import runtime


class BLogger:

    @staticmethod
    def set_base_url(base_url: str):
        """
        Set base_url for the entire Run

            Can also be added in b_logger.config.yaml:
                base_url: 'https://base-url.com'

            Or in command line options:
                --blog_base_url 'https://base-url.com'
        """
        runtime.set_base_url(base_url)

    @staticmethod
    def set_env(env: str):
        """
        Set env for the entire Run

            Can also be added in b_logger.config.yaml:
                    env: 'prod'

            Or in command line options:
                --blog_env 'prod'
        """
        runtime.set_env(env)

    @staticmethod
    def set_browser(browser: RemoteWebDriver | WebDriver | Page):
        """
        Set browser in a browser init fixture or in a test

        If browser init fixture name is in
            ["driver", "page", "selenium_driver", "driver_init", "playwright_page"]
        then it will be detected automatically

        Usage:
            @pytest.fixture()
            def selenium_driver():
                driver = webdriver.Chrome()

                blog.set_browser(driver)

                yield driver

                driver.quit()

            or

            def test_playwright(page): <-- Will be detected automatically
                page.goto(f'https://google.com')
        """
        runtime.set_browser(browser)

    @staticmethod
    def description(description: str):
        """
        Add Test Description
            Can be used as marker @blog.description() as well as function blog.description()
            Usage inside a test expands description inside marker

        Usage:
            @blog.description(
                'Test with base functionality, '
                'this description can be modified inside the test'
            )
            def test_main_functionality():
                blog.description('This description will also be added')
        """
        runtime.apply_description(description)

        return pytest.mark.blog_description(description=description)

    @staticmethod
    def info(**kwargs):
        """
        Leave any info or note about Test or Step before or during execution

        Usage:
            @blog.info(
                first_parameter='param 1',
                second_parameter='param 2'
                meta={'platform': 'linux', 'python_version': 3.12}
            )

            or

            with blog.step('step 2'):
                blog.info(step_param_1='param', step_param_2=123)
        """
        runtime.apply_info(**kwargs)

        return pytest.mark.blog_info(kwargs=kwargs)

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
    def print(data, status: PrintStatus = PrintStatus.NONE):
        """
        Print any message (str, dict, list, object, etc.)
            It will be added to a Current Step as SubStep
            Newlines with \n are supported

        Usage:
            data = {"a": 1, "b": 2}
            blog.print(f'Some important data: {data}')

            blog.print(f'Probably too long str\n'
                        'can be newlined like that')
        """
        runtime.print_message(data, status)

    @staticmethod
    def screenshot(name: str = None, is_error: bool = False):
        """
        Make screenshot
            It will be automatically attached to Test Run and Current Step
            Will do nothing if no browser is used
        """
        runtime.make_screenshot(name, is_error)

    @staticmethod
    def attach(source, name: str = None):
        """
        Attach file or screenshot
            It will be added to Test Run and Current Step
        """
        runtime.attach(source, name)
