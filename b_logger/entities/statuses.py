from enum import Enum


class TestStatus(str, Enum):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    SKIPPED = 'SKIPPED'
    BROKEN = 'BROKEN'
    NONE = 'NONE'


def py_outcome_to_tstatus(outcome):
    return {
        'passed': TestStatus.PASSED,
        'failed': TestStatus.FAILED,
        'skipped': TestStatus.SKIPPED,
        'broken': TestStatus.BROKEN,
    }.get(outcome, TestStatus.NONE)
