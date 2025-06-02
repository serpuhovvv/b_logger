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
@blog.info(info_explanation='You can leave any useful information by using blog.info()',
           meta={'platform': 'linux', 'python_version': 3.12}
)
def test_main_functionality():
    blog.description('This description will also be added')

    with blog.step('step 1'):

        data = {"a": 1, "b": 2}

        blog.print(f'Some important data: {data}')

    with blog.step('step 2'):

        blog.info(step_param_1='param', step_param_2=123)

        blog.print(f'print 2')

        with blog.step('step 2.1'):

            blog.known_bug('Fake Bug for a step', 'https://link-to-your-bug/2.com')

            blog.print(f'print 3')

            with blog.step('step 2.1.1'):
                pass


@pytest.mark.parametrize('py_param', [111, 222])
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

        with blog.step('Raise fake error'):
            assert 1 == 2


@pytest.mark.xfail
@blog.description('This test will also make browser screenshot as it '
                  'found driver automatically '
                  'based on the following possible browser instance fixture names: '
                  '["driver", "page", "selenium_driver", "driver_init", "playwright_page"]')
def test_selenium_without_set_browser(selenium_driver):
    with blog.step('Open any URL'):
        selenium_driver.get(f'https://google.com')

        with blog.step('Raise fake error'):
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
def test_playwright(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        with blog.step('Raise fake error'):
            assert 1 == 2
