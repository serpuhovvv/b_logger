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


class TestParameter(BaseDataModel):
    def __init__(self, name, value):
        self.name = name
        self.value = value


# class TestParametersContainer(BaseDataModel, list):
#     def __init__(self):
#         super().__init__()
#
#     def add_parameter(self, parameter: TestParameter):
#         self.append(parameter)


class TestReport(BaseDataModel):

    def __init__(self, name: str = None):
        # self.id_ = f'test_report_{uuid.uuid4()}'
        self.name: str = name
        self.description: str | None = None
        self.status: TestStatus = TestStatus.NONE
        self.duration: float | None = None
        self.parameters = {}
        self.attachments = []
        self.info = []
        self.preconditions = None
        self.steps = None
        self.error = None
        self.stacktrace = None

    def set_description(self, description: str):
        self.description = description

    def modify_description(self, description: str):
        self.description += f'\n\n{description}'

    def set_status(self, status: TestStatus):
        self.status = status

    def set_duration(self, duration: float):
        self.duration = duration

    def add_parameter(self, name, value):
        self.parameters[name] = value

    def add_attachment(self, attachment: Attachment):
        for attach in self.attachments:
            if attach.name == attachment.name:
                return
        self.attachments.append(attachment)

    def set_steps(self, steps_id):
        self.steps = steps_id

    def set_preconditions(self, preconditions_id):
        self.preconditions = preconditions_id

    def set_error(self, error: TestError):
        self.error = error

    def add_info(self, info_str):
        self.info.append(info_str)

    def get_steps(self):
        steps_path = f'{b_logs_tmp_steps_path()}/{self.steps}.json'
        try:
            steps = StepContainer.from_json(steps_path)
            return steps
        except Exception as e:
            print(f'[WARN] Unable to get steps for {self.name}: {e}')
