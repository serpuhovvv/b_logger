from enum import Enum
from functools import lru_cache


class TestStatus(str, Enum):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    SKIPPED = 'SKIPPED'
    BROKEN = 'BROKEN'
    NONE = 'NONE'


@lru_cache(5)
def py_outcome_to_tstatus(outcome):
    return {
        'passed': TestStatus.PASSED,
        'failed': TestStatus.FAILED,
        'broken': TestStatus.BROKEN,
        'skipped': TestStatus.SKIPPED
    }.get(outcome, TestStatus.NONE)
