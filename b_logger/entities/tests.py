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

    def __init__(self,
                 name: str = None,
                 status: TestStatus = None):
        self.name = name
        self.status: TestStatus = status
        self.duration = None
        self.parameters: TestParametersContainer = TestParametersContainer()
        self.preconditions_id = None
        self.steps_id = None
        self.error = None

    # def set_parameters(self, params):
    #     self.parameters.extend(params)

    def add_parameter(self, name, value):
        self.parameters.add_parameter(TestParameter(name, value))

    def set_steps_id(self, steps_id):
        self.steps_id = steps_id

    def set_preconditions_id(self, preconditions_id):
        self.preconditions_id = preconditions_id
