import pytest
import random
from pytest_playwright.pytest_playwright import Playwright
from selenium import webdriver

from b_logger import blog

blog.set_env('prod')

blog.set_base_url('https://base-url.url')


@pytest.fixture()
def some_fixture():
    with blog.step('aaa'):
        pass

    yield

    with blog.step('bbb'):
        pass


@blog.description(
    'Test with base functionality, '
    'this description can be modified inside the test'
)
@blog.info(
    info_explanation='You can leave any useful information by using blog.info()',
    meta={'platform': 'linux', 'python_version': 3.12}
)
@blog.link(
    first_link='http://aaa.com',
    second_link='http://bbb.com'
)
@blog.known_bug(
    'Known Bug Description or Name',
    'https://link-to-your-bug/1.com'
)
def test_main_functionality(some_fixture):
    blog.description('This description will also be added')

    with blog.step('Step 1', 'Step is expected to pass'):
        data = {"a": 1, "b": 2}
        blog.print(f'Some data: {data}')

        blog.link(third_link='http://ccc.com')

        with blog.step('Step 1.1'):
            step_param_1 = random.randint(1, 100)
            step_param_2 = random.randint(1, 100)

            blog.info(
                step_param_1=step_param_1,
                step_param_2=step_param_2
            )

    with blog.step('Step 2'):
        blog.known_bug('Known Bug for a step', 'https://link-to-your-bug/2.com')

        with blog.step('Step 2.1'):
            pass

            with blog.step('Step 2.11'):
                pass

                with blog.step('Step 2.111'):
                    pass

                    with blog.step('Step 2.1111'):
                        pass


@pytest.mark.parametrize('py_param_1, py_param_2', [(111, 222), (333, 444)])  # <-- These parameters will be added to test automatically
def test_parametrized(py_param_1, py_param_2):
    with blog.step('Step 1'):
        with blog.step('Step 2'):
            with blog.step('Step 3', 'Step is expected to fail'):
                blog.print(py_param_1)
                with blog.step('Step 4'):
                    blog.print(py_param_2)
                assert py_param_1 in [111, 444]


@pytest.fixture()
def selenium_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_size(1920, 1080)

    # blog.set_browser(driver) can be also added here, which is preferred

    yield driver

    driver.quit()


# @pytest.mark.xfail
@blog.description('This test will make browser screenshot as we did blog.set_browser. '
                  'We can also do it in "selenium_driver" fixture')
@blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')
def test_selenium_with_set_browser(selenium_driver):
    blog.set_browser(selenium_driver)

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2


# @pytest.mark.xfail
@blog.description('This test will also make browser screenshot as it '
                  'found driver automatically '
                  'based on the following possible browser instance fixture names: '
                  '["driver", "page", "selenium_driver", "driver_init", "playwright_page"]')
def test_selenium_without_set_browser(selenium_driver):  #  <-- Will be detected automatically

    blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2


@pytest.fixture()
def playwright_page(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)

    context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # blog.set_browser(page) can also be added here, which is preferred

    yield page

    browser.close()


# @pytest.mark.xfail
def test_playwright(playwright_page):  #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        with blog.step('Raise fake error to check error screenshot'):
            print(empty_variable)
