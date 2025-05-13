"""
version: 1.0.0

*conftest.py*

from b_logger import blog

pytest_plugins = ["b_logger.plugin"]

"""

from .blog import BLogger

blog = BLogger()

# def apply_decorators(*decorators):
#     def meta_decorator(func):
#         for decorator in reversed(decorators):
#             func = decorator(func)
#         return func
#     return meta_decorator
