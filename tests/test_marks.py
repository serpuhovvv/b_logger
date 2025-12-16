import pytest

from b_logger import blog


@pytest.mark.smoke('420', every='day')
def test_mark():
    pass


@pytest.mark.xfail(reason='gycha')
def test_should_skip(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error'):
        print(empty_variable)


@pytest.mark.xfail
def test_should_pass(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')


@pytest.mark.xfail(strict=True)
def test_should_fail(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')


@pytest.mark.xfail(raises=RuntimeError)
def test_should_skip_2(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error'):
        raise RuntimeError('No reason')


@pytest.mark.xfail(raises=RuntimeError)
def test_should_fail_2(playwright_page):
    with blog.step('Open any URL'):
        playwright_page.goto(f'https://google.com')

        c2 = playwright_page.context.browser.new_context()
        p2 = c2.new_page()
        p2.bring_to_front()
        p2.goto(f'https://en.wikipedia.org/wiki/Jalape%C3%B1o')

    with blog.step('Raise fake error'):
        raise AssertionError('No reason')