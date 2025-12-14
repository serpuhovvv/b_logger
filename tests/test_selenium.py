import pytest

from b_logger import blog


@blog.description(
    'This test will make browser screenshot as we did blog.set_browser. '
    'We can also do it in "selenium_driver" fixture'
)
@blog.info(
    run_requirement='To run this test you\'ll need to download chromedriver and put it in your python folder'
)
def test_selenium_with_set_browser(selenium_driver):
    with blog.step('Set Browser'):
        blog.set_browser(selenium_driver)

    with blog.step('Open any URL'):
        selenium_driver.get(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error to check error screenshot'):
        assert 1 == 2


@blog.description('This test will also make browser screenshot as it found driver automatically '
                  'based on the following possible browser instance fixture names: "driver", "page", "selenium_driver", "driver_init", "playwright_page"')
def test_selenium_without_set_browser(selenium_driver):  #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        selenium_driver.get(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

        with blog.step('Raise fake error to check error screenshot'):
            print(empty_variable)
