"""
version: 1.0.0

*conftest.py*

from b_logger import blog

"""

from .blog import BLogger

__all__ = ['blog']

blog = BLogger()
