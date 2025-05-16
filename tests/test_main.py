import pytest
from pytest_playwright.pytest_playwright import Playwright
from selenium import webdriver

from b_logger import blog

blog.set_env('prod')

blog.set_base_url('https://base-url.url')


@pytest.fixture()
def selenium_driver():
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)

    blog.set_browser(driver)

    yield driver

    driver.quit()


@pytest.fixture()
def playwright_page(playwright: Playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    blog.set_browser(page)

    yield page

    browser.close()


@blog.description(
    'Test with base functionality, '
    'this description is more priority than the one below'
)
@blog.known_bug(
    'Fake Bug Description',
    'https://link-to-your-bug.com'
)
@blog.param('Some Param you want to add', 'Param Value')
def test_main_functionality():
    blog.description('Test with base functionality, this description is less priority')

    blog.param('Some dynamic param', 222)

    blog.info(f'Just some helpful info')

    with blog.step('step 1'):

        blog.print(f'print 1')

    with blog.step('step 2'):
        pass

        with blog.step('step 2.1'):

            blog.print(f'print 2')

            with blog.step('step 2.3'):
                pass


@pytest.mark.parametrize('paramchik', [111, 222])
def test_parametrized(paramchik):
    with blog.step('step 1'):
        blog.print(paramchik)

        with blog.step('step 2'):
            pass


@pytest.mark.xfail
def test_selenium(selenium_driver):
    with blog.step('step 1'):
        selenium_driver.get(f'https://google.com')

        with blog.step('step 2'):
            assert 1 == 2


@pytest.mark.xfail
def test_playwright(playwright_page):
    with blog.step('step 1'):
        playwright_page.goto(f'https://google.com')

        with blog.step('step 2'):
            assert 1 == 2
