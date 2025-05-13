from enum import Enum


class TestStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    BROKEN = 'broken'
    NONE = 'none'


def py_outcome_to_tstatus(outcome):
    return {
        'passed': TestStatus.PASSED,
        'failed': TestStatus.FAILED,
        'skipped': TestStatus.SKIPPED,
        'broken': TestStatus.BROKEN,
    }.get(outcome, TestStatus.NONE)