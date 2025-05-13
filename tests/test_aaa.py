import pytest

from b_logger import blog


def test_01():
    blog.add_parameter('aaa', 123)

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
