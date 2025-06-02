import uuid
from typing import Any

from b_logger.entities.attachments import Attachment
from b_logger.entities.steps import StepContainer
from b_logger.entities.statuses import TestStatus
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import b_logs_tmp_steps_path


class TestError(BaseDataModel):
    def __init__(self, exc, stacktrace):
        self.exception = exc
        self.stacktrace = stacktrace


# class TestInfo(BaseDataModel):
#     def __init__(self):
#         self.description = None
#         self.parameters = {}
#         self.known_bugs = []
#         self.other = []
#
#     def add_parameter(self, key, value):
#         self.parameters[key]= value


class TestReport(BaseDataModel):

    def __init__(self, name: str = None):
        self.name: str = name
        self.status: TestStatus = TestStatus.NONE
        self.duration: float | None = None
        self.description: str | None = None
        self.parameters = {}
        self.info = {}
        self.attachments = []
        self.known_bugs = []
        self.preconditions = None
        self.steps = None
        self.error = None
        self.stacktrace = None

    def set_status(self, status: TestStatus):
        self.status = status

    def set_duration(self, duration: float):
        self.duration = duration

    def set_preconditions(self, preconditions_id):
        self.preconditions = preconditions_id

    def set_steps(self, steps_id):
        self.steps = steps_id

    def set_error(self, error: str):
        self.error = error

    def set_stacktrace(self, stacktrace: str):
        self.stacktrace = stacktrace

    def set_description(self, description: str):
        self.description = description

    def modify_description(self, description: str):
        self.description += f'\n\n{description}'

    def add_parameter(self, name, value):
        self.parameters[name] = value

    def add_known_bug(self, bug):
        self.known_bugs.append(bug)

    def add_info(self, info: dict):
        for key, value in info.items():
            if key in self.info:
                existing = self.info[key]
                if not isinstance(existing, list):
                    self.info[key] = [existing]
                self.info[key].append(value)
            else:
                self.info[key] = value

    def add_attachment(self, attachment: Attachment):
        for attach in self.attachments:
            if attach.name == attachment.name:
                return
        self.attachments.append(attachment)

    def get_steps(self):
        steps_path = f'{b_logs_tmp_steps_path()}/{self.steps}.json'
        try:
            steps = StepContainer.from_json(steps_path)
            return steps
        except Exception as e:
            print(f'[WARN] Unable to get steps for {self.name}: {e}')
