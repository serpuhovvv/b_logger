"""
Copyright 2025 Serg Pudikov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pytest

from pathlib import Path
from typing import Union, BinaryIO
from contextlib import contextmanager

from b_logger.entities.steps import Step
from b_logger.entities.exceptions import possible_exceptions
from b_logger.integrations import Integrations
from b_logger.plugin import runtime


class BLogger:

    @staticmethod
    def set_env(env: str):
        """
        Set env for the entire Run

        Can also be added in blog.config.yaml:
            env: 'prod'

        Or via command line options:
            --blog-env 'prod'
        """
        runtime.set_env(env)

    @staticmethod
    def set_base_url(base_url: str):
        """
        Set base_url for the entire Run

        Can also be added in blog.config.yaml:
            base_url: 'https://base-url.com'

        Or via command line options:
            --blog-base-url 'https://base-url.com'
        """
        runtime.set_base_url(base_url)

    @staticmethod
    def set_browser(browser: "RemoteWebDriver | WebDriver | Page"):
        """
        Set browser in a browser init fixture or in a test

        If browser init fixture name is "driver", "page", "selenium_driver", "driver_init", "playwright_page"
            then it will be detected and applied automatically.

        If browser is set it will also automatically make error screenshots on test fails and attach them to current step and error info.

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
        Will be added to the Overview Tab

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
        Leave any important info or note about Test or Step
        Will be added to the Overview Tab and Current Step

        Can be used as marker @blog.info(k=v) as well as function blog.info(k=v)

        k is a name of an info block
        v supports any data type, but {} is most readable and convenient

        Any amount of info blocks is allowed: @blog.info(k=v, k=v, k=v, ...)

        Usage:
            @blog.info(                             <-- Will be added for a Test
                meta={'platform': 'linux', 'python_version': 3.12}
                additional_parameters=['param 1', 'param 2'],
                some_info='some info',
            )
            def test_main_functionality():
                blog.info(a='a')                    <-- Will be added for a Test

                with blog.step('Step 1'):
                    blog.info(                      <-- Will be added for a Test and a Step
                        step_1_info={'b': 2, 'c': 3}
                    )
        """
        runtime.apply_info(**kwargs)

        return pytest.mark.blog_info(kwargs=kwargs)

    @staticmethod
    def link(**kwargs):
        """
        Attach links to Test or Step
        Will be added to the Overview Tab and Current Step

        Can be used as marker @blog.link(k=v) as well as function blog.link(k=v)

        k is a name of a link
        v is a URL

        Any amount of links is allowed: @blog.link(k=v, k=v, k=v, ...)

        Usage:
            @blog.link(
                first_link='http://aaa.com',
                second_link='http://bbb.com'
            )
            def test_main_functionality():
                blog.link(third_link='http://ccc.com')
        """
        runtime.apply_link(**kwargs)

        return pytest.mark.blog_link(kwargs=kwargs)

    @staticmethod
    def known_bug(url: str = None, description: str = None):
        """
        Add known bug for Test or Step
        Will be added to the Overview Tab and Current Step

        Usage:
            @blog.known_bug(
                'https://link-to-your-bug/1.com',
                'Test Bug 1'
            )
            def test_main_functionality():
                blog.known_bug(description='Test Bug 2')

                with blog.step('Step Title'):
                    blog.known_bug('https://link-to-your-bug/3.com')
        """
        runtime.apply_known_bug(url, description)

        return pytest.mark.blog_known_bug(url=url, description=description)

    @staticmethod
    @contextmanager
    def step(title: str, expected: str = None):
        """
        Wrap a code block into a step.
        Will be displayed in Setup, Steps and Teardown blocks depending on a test stage.

        Info, Known Bugs, Links, Screenshots, Prints, Attachments will be added to a current step if made inside a step context.

        Usage:
            with blog.step('Step Title', 'Expected Result'):
                ...
        """
        with Integrations.step(title, expected):

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
    def print(data):
        """
        Print any message (str, dict, list, object, etc.)
        Will be added to a Current Step and stdout.txt

        Usage:
            data = {"a": 1, "b": 2}
            blog.print(f'Some important data: {data}')

            blog.print(f'Probably too long str\n'
                        'can be newlined like that')
        """
        runtime.print_message(data)

    @staticmethod
    def screenshot(name: str = None, is_error: bool = False):
        """
        Make screenshot

        Will be added to the Attachments Tab and Current Step
        Will do nothing if no browser is used

        is_error flag adds "err_scr_" prefix to a scr name

        Usage:
            blog.screenshot('scr_name')
            blog.screenshot('err_scr_name', True)
        """
        runtime.make_screenshot(name, is_error)

    @staticmethod
    def attach(content: Union[bytes, Path, BinaryIO, str, dict, list, int, float, bool, None], name: str = None):
        """
        Attach file or data
        Will be added to the Attachments Tab and Current Step

        Add extension to file name to save as a particular type. Example: 'excel_file.xlsx'

        Usage:
            blog.attach({"a": 1, "b": 2}, 'some_data')
            blog.attach(Path('path/to/your/file.ext'))
            blog.attach(excel_data, 'excel_file.xlsx')
        """
        runtime.attach(content, name)
