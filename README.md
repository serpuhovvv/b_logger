# BLogger — Pytest Logging Plugin

---

### Overview

BLogger is a Pytest plugin for enhanced test logging and reporting.  
It supports structured test steps, descriptions, info notes, known bugs, and automatic screenshots.  
Works seamlessly with Selenium WebDriver and Playwright Page instances.

### Features

- Set global **base URL**, **environment**, and **browser** instance (Selenium or Playwright).  
- Add/update **test descriptions** dynamically.
- Log any **info** during tests or steps.  
- Mark tests/steps with **known bugs** and optional bug tracker URLs.
- Print messages attached to current step (supports multiline and complex data).  
- Take and attach **screenshots** automatically on demand or on errors.  
- Attach files or arbitrary data to steps.

### Installation

```bash
pip install b_logger
```

### Setup
Add blog.config.yaml file to the root of your project.\
Bare minimum for everything to work: 
```yaml
project_name: "Project Name"
```

### Usage examples

You may just read through this test file and understand common usage.

```python
import pytest
from pytest_playwright.pytest_playwright import Playwright
from selenium import webdriver

from b_logger import blog


blog.set_env('prod')


blog.set_base_url('https://base-url.url')


@blog.description(
    'Test with base functionality, '
    'this description can be modified inside the test'
)
@blog.known_bug(
    'Fake Bug Description or Name',
    'https://link-to-your-bug/1.com'
)
@blog.info(
    info_explanation='You can leave any useful information by using blog.info()',
    meta={'platform': 'linux', 'python_version': 3.12}
)
def test_main_functionality():
    
    blog.description('This description will also be added')

    with blog.step('Step 1'):

        data = {"a": 1, "b": 2}

        blog.print(f'Some important data: {data}')

        with blog.step('Step 1.1'):
    
            blog.info(step_param_1='param', step_param_2=123)
    
            with blog.step('Step 1.1.1'):
    
                blog.known_bug('Fake Bug for a step', 'https://link-to-your-bug/2.com')
    
            with blog.step('Step 1.1.2'):
                pass


@pytest.mark.parametrize('py_param', [111, 222]) # <-- These parameters will be added to test automatically
def test_parametrized(py_param):
    with blog.step('step 1'):

        blog.print(py_param)

        with blog.step('step 2'):
            pass


@pytest.fixture()
def selenium_driver():
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)

    # blog.set_browser(driver) can be also added here

    yield driver

    driver.quit()


@pytest.mark.xfail
@blog.description('This test will make browser screenshot as we did blog.set_browser. '
                  'We can also do it in "selenium_driver" fixture')
@blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')
def test_selenium_with_set_browser(selenium_driver):

    blog.set_browser(selenium_driver)

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2


@pytest.mark.xfail
@blog.description('This test will also make browser screenshot as it '
                  'found driver automatically '
                  'based on the following possible browser instance fixture names: '
                  '["driver", "page", "selenium_driver", "driver_init", "playwright_page"]')
def test_selenium_without_set_browser(selenium_driver): #  <-- Will be detected automatically
    
    blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2


@pytest.fixture()
def playwright_page(playwright: Playwright):
    browser = playwright.chromium.launch()

    context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # blog.set_browser(page) can also be added here

    yield page

    browser.close()


@pytest.mark.xfail
def test_playwright(playwright_page): #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2
```

### Documentation on Methods

```python
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

            Can also be added in blog.config.yaml:
                base_url: 'https://base-url.com'

            Or in command line options:
                --blog_base_url 'https://base-url.com'
        """
        runtime.set_base_url(base_url)

    @staticmethod
    def set_env(env: str):
        """
        Set env for the entire Run

            Can also be added in blog.config.yaml:
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

            with blog.step('Step 1'):
                blog.info(
                    step_param_1='param',
                    step_param_2=123
                )
        """
        runtime.apply_info(**kwargs)

        return pytest.mark.blog_info(kwargs=kwargs)

    @staticmethod
    def known_bug(description: str, url: str = None):
        """
        Mark the test as having a known bug or apply it to current step.

        Usage:
            @blog.known_bug(
                'Fake Bug Description or Name',
                'https://link-to-your-bug/1.com'
            )

            or

            with blog.step('Step 1'):
                blog.known_bug('Fake Bug for a step', 'https://link-to-your-bug/2.com')
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

        Usage:
            blog.screenshot('scr_name')
        """
        runtime.make_screenshot(name, is_error)

    @staticmethod
    def attach(source, name: str = None):
        """
        Attach file or screenshot
            It will be added to Test Run and Current Step
        """
        runtime.attach(source, name)
```