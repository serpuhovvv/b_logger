from b_logger.entities.steps import Step, StepContainer


class Precondition(Step):
    def __init__(self):
        super().__init__()


class PreconditionsContainer(StepContainer):
    def __init__(self):
        super().__init__()
