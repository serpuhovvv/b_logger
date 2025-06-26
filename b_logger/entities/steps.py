import traceback
from contextlib import contextmanager, ContextDecorator
import uuid
from enum import Enum
from filelock import FileLock

from b_logger.entities.attachments import Attachment
from b_logger.entities.prints import Print
from b_logger.utils.paths import b_logs_tmp_path, b_logs_tmp_steps_path
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.formatters import format_exc, format_tb


class StepStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    WARNING = 'warning'
    NONE = 'none'


# class StepManager:
#     def __init__(self):
#         self.current_step_id = None
#         self.failed = False
#
#     def set_current_step(self, step_id):
#         self.current_step_id = step_id


class StepError(BaseDataModel):
    def __init__(self, exc, tb=None):
        self.exc = format_exc(exc)
        self.tb = tb or format_tb(traceback.format_exc(4))


class Step(BaseDataModel):
    def __init__(self,
                 title: str = None,
                 status: StepStatus = None,
                 expected: str = None
                 ):
        self.id = f'step_{uuid.uuid4()}'
        self.title = title
        self.status = status
        self.expected = expected
        self.parent_id = None
        self.error: StepError | None = None
        self.info = {}
        self.attachments = []
        self.known_bugs = []
        self.steps = []

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

    def add_info(self, info):
        for key, value in info.items():
            if key in self.info:
                existing = self.info[key]
                if not isinstance(existing, list):
                    self.info[key] = [existing]
                self.info[key].append(value)
            else:
                self.info[key] = value

    def add_known_bug(self, bug):
        self.known_bugs.append(bug)

    def get_sub_steps(self, as_dict: bool = False):
        if as_dict:
            return {step.id: step for step in self.steps}
        else:
            return self.steps


class StepContainer(BaseDataModel, dict):
    def __init__(self):
        super().__init__()
        self.container_id = f'steps_{uuid.uuid4()}'
        self.current_step_id = None
        self.failed = False
        self.current_stage = 'setup'
        self['setup'] = []
        self['call'] = []
        self['teardown'] = []

    def set_current_step(self, step_id):
        self.current_step_id = step_id

    def add_step(self, step: Step | Print):
        cur_stg = self.get(self.current_stage)
        cur_stg.append(step)

    def get_all_steps(self) -> list[Step]:
        return self.get('setup', []) + self.get('call', []) + self.get('teardown', [])

    def get_current_step(self) -> Step | None:
        return self.get_step_by_id(self.current_step_id)

    def get_step_by_id(self, step_id: str) -> Step | None:
        for step in self.get_all_steps():
            found = self._recursive_search(step, step_id)
            if found:
                return found
        return None

    @staticmethod
    def _recursive_search(step: Step, step_id: str) -> Step | None:
        if step.id == step_id:
            return step
        for sub_step in step.steps:
            if not sub_step.id.startswith('print_'):
                found = StepContainer._recursive_search(sub_step, step_id)
                if found:
                    return found
        return None

    def save_json(self, file_name=None):
        root = f'{b_logs_tmp_steps_path()}'
        if file_name:
            path = f'{root}/{file_name}'
        else:
            path = f'{root}/{self.container_id}'
        with FileLock(f'{path}.lock'):
            self.to_json_file(path)
