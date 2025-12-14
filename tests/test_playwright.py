import pytest

from b_logger import blog


def test_playwright_with_set_browser(playwright_page):
    with blog.step('Set Browser'):
        blog.set_browser(playwright_page)

    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error to check auto error screenshot'):
        raise AssertionError('Fake Error')


def test_playwright_without_set_browser(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error to check auto error screenshot'):
        print(empty_variable)


def test_playwright_autodetect_positive(page):  #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        page.goto(f'https://google.com')

        c2 = page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')


def test_playwright_autodetect_negative(page):  #  <-- Will be detected automatically
    with blog.step('Open any URL'):
        page.goto(f'https://google.com')

        c2 = page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error to check error screenshot'):
        raise AssertionError('Fake Error')