import uuid
from enum import Enum

from b_logger.utils.basedatamodel import BaseDataModel


class PrintStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    WARNING = 'warning'
    NONE = 'none'


class Print(BaseDataModel):
    def __init__(self, data, status: PrintStatus):
        self.id_ = f'print_{uuid.uuid4()}'
        self.title = data
        self.status = status
        self.parent_id = None

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id