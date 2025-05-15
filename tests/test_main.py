import pytest

from selenium import webdriver
from playwright.sync_api import sync_playwright

from b_logger import blog

blog.set_env('prod')

blog.set_base_url('https://base-url.url')


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()

    blog.set_browser(driver)

    yield driver

    driver.quit()


@pytest.fixture()
def playwright_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()

    page = browser.new_page()

    blog.set_browser(page)

    yield page

    browser.close()


def test_main_functionality():
    blog.param('aaa', 123)

    blog.info(f'some info')

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
def test_selenium(driver):
    with blog.step('step 1'):
        driver.get(f'google.com')

        with blog.step('step 2'):
            assert 1 == 2


