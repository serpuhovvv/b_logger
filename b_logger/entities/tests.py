import uuid
from typing import Any

from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.entities.statuses import TestStatus


class TestError(BaseDataModel):
    def __init__(self, e, tb):
        self.exc = e
        self.tb = tb


class TestParameter(BaseDataModel):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class TestParametersContainer(BaseDataModel, list):
    def __init__(self):
        super().__init__()

    def add_parameter(self, parameter: TestParameter):
        self.append(parameter)


class TestReport(BaseDataModel):

    def __init__(self, name: str = None):
        self.id_ = uuid.uuid4()
        self.name = name
        self.status: TestStatus = None
        self.duration = None
        self.parameters = []
        # self.attachments = {}
        self.preconditions_id = None
        self.steps_id = None
        self.error = None
        self.stacktrace = None

    def set_status(self, status: TestStatus):
        self.status = status

    def set_duration(self, duration: float):
        self.duration = duration

    def add_parameter(self, name, value):
        self.parameters.append(TestParameter(name, value))

    def set_steps_id(self, steps_id):
        self.steps_id = steps_id

    def set_preconditions_id(self, preconditions_id):
        self.preconditions_id = preconditions_id

    def set_error(self, error: TestError):
        self.error = error
