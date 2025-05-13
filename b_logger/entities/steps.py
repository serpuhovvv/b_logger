import traceback
from contextlib import contextmanager, ContextDecorator
import uuid
from enum import Enum
from filelock import FileLock

from b_logger.utils.paths import tmp_logs_path
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.formatters import format_exc, format_tb


class StepStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    WARNING = 'warning'
    NONE = 'none'


class StepManager:
    def __init__(self):
        self.current_step_id = None

    # def drop_current_step(self):
    #     self.current_step = None


class StepError(BaseDataModel):
    def __init__(self, exc, tb=None):
        self.exc = format_exc(exc)
        self.tb = tb or format_tb(traceback.format_exc(4))


class Step(BaseDataModel):
    def __init__(self,
                 id_=None,
                 title=None,
                 status: StepStatus = None
                 ):
        if id_:
            self.id = id_
        else:
            self.id = uuid.uuid4()

        self.title = title
        self.status = status
        self.parent_id = None
        self.steps = []
        self.errors = []

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id

    def set_status(self, status: StepStatus):
        self.status = status

    def add_error(self, error: StepError):
        self.errors.append(error)

    def add_sub_step(self, step):
        self.steps.append(step)

    def get_sub_steps(self, as_dict: bool = False):
        if as_dict:
            return {step.id: step for step in self.steps}
        else:
            return self.steps


class StepContainer(BaseDataModel, list):
    def __init__(self):
        super(list).__init__()
        self.container_id = f'steps_{uuid.uuid4()}'

    def add_step(self, step):
        self.append(step)

    def get_step_by_id(self, step_id) -> Step:
        step_map = {step.id: step for step in self}
        return step_map.get(step_id)

    def save_json(self, path=None):
        if not path:
            path = f'{tmp_logs_path()}/steps/{self.container_id}'
        with FileLock(f'{path}.lock'):
            self.to_json_file(path)
