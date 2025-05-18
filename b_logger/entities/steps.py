import traceback
from contextlib import contextmanager, ContextDecorator
import uuid
from enum import Enum
from filelock import FileLock

from b_logger.entities.attachments import Attachment
from b_logger.utils.paths import b_logs_tmp_path
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.formatters import format_exc, format_tb


class StepStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    WARNING = 'warning'
    NONE = 'none'


class StepManager:
    def __init__(self):
        self.current_step_id = None
        self.failed = False

    def set_current_step(self, step_id):
        self.current_step_id = step_id


class StepError(BaseDataModel):
    def __init__(self, exc, tb=None):
        self.exc = format_exc(exc)
        self.tb = tb or format_tb(traceback.format_exc(4))


class Step(BaseDataModel):
    def __init__(self, title=None,
                 status: StepStatus = None
                 ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.status = status
        self.parent_id = None
        self.attachments = []
        self.steps = []
        self.error: StepError | None = None

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id

    def add_attachment(self, attachment: Attachment):
        self.attachments.append(attachment)

    def set_status(self, status: StepStatus):
        self.status = status

    def set_error(self, error: StepError):
        self.error = error

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

    def get_step_by_id(self, step_id) -> Step | None:
        for step in self:
            if getattr(step, 'id', None) == step_id:
                return step

            nested_steps = getattr(step, 'steps', None)
            if isinstance(nested_steps, (list, StepContainer)):
                found = StepContainer.get_step_by_id(nested_steps, step_id)
                if found:
                    return found

        return None

    def save_json(self, path=None):
        if not path:
            path = f'{b_logs_tmp_path()}/steps/{self.container_id}'
        with FileLock(f'{path}.lock'):
            self.to_json_file(path)
