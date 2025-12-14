import pytest
from playwright.sync_api import Playwright
from selenium import webdriver

from b_logger import blog


blog.set_env('prod1')

blog.set_base_url('https://base-url-1.url')


def pytest_configure():
    blog.set_env('prod2')

    blog.set_base_url('https://base-url-2.url')



@pytest.fixture()
def selenium_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_size(1920, 1080)

    # blog.set_browser(driver) can be also added here, which is preferred

    yield driver

    driver.quit()


@pytest.fixture()
def playwright_page(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)

    context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # blog.set_browser(page) can also be added here, which is preferred

    yield page

    page.close()
    browser.close()