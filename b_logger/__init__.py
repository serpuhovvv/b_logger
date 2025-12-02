"""
*conftest.py*

from b_logger import blog

For full documentation, please visit GitHub: https://github.com/serpuhovvv/b_logger

"""

from .blog import BLogger

__all__ = ['blog']

blog: BLogger = BLogger()
