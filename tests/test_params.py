import pytest
import random

from b_logger import blog


class ABC:
    def __init__(self):
        super().__init__()
        self.a = 123

    def some_method(self):
        pass


class CBA(ABC):
    def __init__(self):
        super().__init__()
        self.a = 321

    def some_method(self):
        pass


@pytest.fixture()
def jumba():
    with blog.step('jamba'):
        pass


@pytest.mark.parametrize("strategy_class", [ABC, CBA])
def test_with_classes_as_params(strategy_class):
    blog.description(f'This test checks how classes are displayed in parameters')

    blog.print({'a': ABC})


@pytest.mark.parametrize('py_param_1, password', [(111, 222), (777, f'qase.link/and/one_more.link')])  # <-- These parameters will be added to test automatically
def test_parametrized(jumba, py_param_1, password):
    with blog.step('Pre'):
        pass
    with blog.step('Step 1'):
        with blog.step('Step 2'):
            with blog.step('Step 3', 'Step is expected to fail'):
                with blog.step('Step 4'):
                    blog.print(py_param_1)
                    blog.print(password)

                x = random.choice([111, 222, 444, 555, 666, 777, 888, 999])
                assert py_param_1 == x
