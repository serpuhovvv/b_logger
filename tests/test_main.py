from pathlib import Path

import pytest
import random
from pytest_playwright.pytest_playwright import Playwright
from selenium import webdriver

from b_logger import blog

blog.set_env('prod')

blog.set_base_url('https://base-url.url')


class ABC:
    def __init__(self):
        super().__init__()
        self.a = 123

    def aaa(self):
        pass


class CBA:
    def __init__(self):
        super().__init__()
        self.a = 123

    def aaa(self):
        pass


@pytest.mark.regression
@blog.link(jira_link="https://admortgage.atlassian.net/browse/QA-234")
@pytest.mark.parametrize("strategy_class", [ABC, CBA])
def test_tasks(strategy_class):
    blog.info(title=f"Create a new task and verify fields via")
    blog.description(f"This test verifies the creation of a new task via and checks that all task fields are correctly filled.")

    blog.print({'a': CBA})

    link = ''

    blog.link(qase_link=link, name='case_for_allure')


@pytest.fixture()
def some_fixture():
    with blog.step('aaa'):
        blog.print('aaa')

    yield

    with blog.step('bbb'):
        blog.print('bbb')


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
    'https://link-to-your-bug/1.com',
    'Test Bug 1'
)
def test_main_functionality(some_fixture):
    blog.description('This description will also be added')

    with blog.step('Step 1', 'Step is expected to pass'):
        data = {"a": 1, "b": 2}
        blog.print(f'Some data: {data}')

        with blog.step('Step 1.1'):
            step_param_1 = random.randint(1, 100)
            step_param_2 = random.randint(1, 100)

            blog.info(
                step_param_1=step_param_1,
                step_param_2=step_param_2
            )

    with blog.step('Step 2'):
        blog.link(third_link='http://ccc.com')

        with blog.step('Step 2.1'):
            blog.known_bug(description='Test Bug 2')
            blog.known_bug('https://link-to-your-bug/3.com')

            with blog.step('Step 2.11'):
                pass

                with blog.step('Step 2.111'):
                    pass

                    with blog.step('Step 2.1111'):
                        pass


@pytest.mark.parametrize('py_param_1, py_param_2', [(f'qase.link/and/one_more.link', 222), (333, f'qase.link/and/one_more.link')])  # <-- These parameters will be added to test automatically
def test_parametrized(selenium_driver, py_param_1, py_param_2):
    with blog.step('Step 1'):
        selenium_driver.get(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')
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


@blog.description('This test will make browser screenshot as we did blog.set_browser. '
                  'We can also do it in "selenium_driver" fixture')
@blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')
def test_selenium_with_set_browser(selenium_driver):
    blog.set_browser(selenium_driver)

    excel_bytes = (
        b'PK\x03\x04\x14\x00\x00\x00\x08\x00\xbb\x9c\xb2Z\x07AMb\x81\x00\x00\x00\xa1\x00\x00\x00\x10\x00\x00\x00'
        b'[Content_Types].xml\x8d\x92\xcbj\xc30\x10E\xf7}\x8a\xdd\xd3$\x08\x82\x9d\xb4\xf5\r\xea\xce\xd4R\xd3\x0e'
        b'H\x92\xd2\xb4\xb7\x1b\xb2$<\x7f\x1f\xe4\xed\x1e\x02\x19\xd2\xa4\x89B\x88\x93p\x8f\xf4\xabW]\xe9b\xa7\x17'
        b'q\xa4k\xb2\xc4\xa1\xd8\xaa\xf7\x1cA\xde\xa6\xc4\x9d\xa8\x8aS\x98\xc1\xf3\xa0\xdb\x04v\x91\xf5\xf9\x15\xda'
        b'\x12Y\x08\x15\xf5\xc4\xb6qf\xae\x89p\x84\xf6\xa0$\xd2\xc1\xbd\xb8J\xd0\xa8\xae\xb8\x02\xfa\xa9a\xf9\xf8'
        b'\x8f\xf6\x90\x8a\x8d\xd8\xba\x80\xd4\xef\xa7\x1f\x00PK\x03\x04\x14\x00\x00\x00\x08\x00\xbb\x9c\xb2Z\xb7O'
        b'\xe3\xdcM\x01\x00\x00\xda\x02\x00\x00\x13\x00\x00\x00xl/_rels/workbook.xml.rels\x8d\x92\xc1J\xc30\x10E\xf7'
        b'\x7fE\xf7\xa9$\x08\x82\xbd\xb4\xf5\rZ\xd7\xb6\x89\xae\x04\x1b\xb7\x9c\xf4\xb6E\xb2\xb1H\xf2\xe1\x87\x9f'
        b'\x03cJb\xb2p$\xf5\x8b\x8b\x95\xfa\x9a\xf7\x19\xea\x94m\xb6\x08\xd1\xc5\xa3\xce\x80\xb8\x02\x99\x9a\xf4\xc6'
        b'\x8a\xa8m\x18\x96!\xc3\xfd\xab\xe8\xa5\xa6\xed\xa5\xb2d\xb4\x80\xd4\xb4R\x9d\xf5q\xc6\x1f\xdb\x97\xd7\xd6'
        b'\x7f\xd1\xdaR\xda\xd6\xf4\x0fPK\x03\x04\x14\x00\x00\x00\x08\x00\xbb\x9c\xb2Z\xab\xb1\x90\x0b\x14\x01\x00'
        b'\x00\xcb\x02\x00\x00\x10\x00\x00\x00xl/workbook.xml\x8d\x92M\x8b\xc30\x10E\xf7\xbd\x8a\xdd\xd3$\x08\x82\x9d'
        b'\xb4\xf5\r\xa2\xce\xd4R\xd3\x0eH\x92\xd2\xb4\xb7\x1b\xb2$<\x7f\x1f\xe4\xed\x1e\x02\x19\xd2\xa4\x89B\x88'
        b'\x93p\x8f\xf4\xabW]\xe9b\xa7\x17q\xa4k\xb2\xc4\xa1\xd8\xaa\xf7\x1cA\xde\xa6\xc4\x9d\xa8\x8aS\x98\xc1\xf3'
        b'\xa0\xdb\x04v\x91\xf5\xf9\x15\xda\x12Y\x08\x15\xf5\xc4\xb6qf\xae\x89p\x84\xf6\xa0$\xd2\xc1\xbd\xb8J\xd0'
        b'\xa8\xae\xb8\x02\xfa\xa9a\xf9\xf8\x8f\xf6\x90\x8a\x8d\xd8\xba\x80\xd4\xef\xa7\x1f\x00PK\x01\x02\x14\x03'
    )
    blog.attach(excel_bytes, 'excel_file.xlsx')

    blog.attach(Path(r"D:\SLAI\Docs\OPTION 2 Rent a ComfyUI Server.pdf"), 'pdf_file')
    blog.attach('a', 'text_file')

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

        with blog.step('Raise fake error to check error screenshot'):
            assert 1 == 2


@blog.description('This test will also make browser screenshot as it '
                  'found driver automatically '
                  'based on the following possible browser instance fixture names: '
                  '["driver", "page", "selenium_driver", "driver_init", "playwright_page"]')
@pytest.mark.smoke('420', every='day')
def test_selenium_without_set_browser(selenium_driver):  #  <-- Will be detected automatically
    blog.info(run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder')

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

        with blog.step('Raise fake error to check error screenshot'):
            print(empty_variable)


@pytest.fixture()
def playwright_page(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)

    context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # blog.set_browser(page) can also be added here, which is preferred

    yield page

    browser.close()


@pytest.mark.xfail
def test_playwright(playwright_page):  #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

        with blog.step('Raise fake error to check error screenshot'):
            print(empty_variable)
