"""
version: 1.0.0

*conftest.py*

from b_logger import blog

"""

from .blog import BLogger
from .entities.prints import PrintStatus

blog = BLogger()
