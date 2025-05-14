import pytest

from b_logger import blog

blog.set_env('prod')

blog.set_base_url('https://base-url.url')


def test_01():
    blog.param('aaa', 123)

    with blog.step('step 1'):
        pass

    with blog.step('step 2'):
        pass


@pytest.mark.parametrize('paramchik', [111, 222])
def test_02(paramchik):
    with blog.step('step 1'):

        with blog.step('step 2'):
            pass


def test_03():
    with blog.step('step 1'):

        with blog.step('step 2'):
            assert 1 == 2
