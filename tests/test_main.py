import pytest
import random

from b_logger import blog


@pytest.fixture()
def some_fixture():
    with blog.step('Precondition'):
        blog.print('aaa')

    yield

    with blog.step('Postcondition'):
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

            with blog.step('Step 2.11'):
                blog.known_bug('https://link-to-your-bug/3.com')

                with blog.step('Step 2.111'):
                    pass

                    with blog.step('Step 2.1111'):
                        pass
