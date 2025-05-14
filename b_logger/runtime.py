import traceback

from b_logger.entities.reports import Report
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.entities.tests import TestReport, TestStatus, TestError
from b_logger.entities.steps import Step, StepStatus, StepError, StepManager, StepContainer
from b_logger.generators.html_gen import HTMLGenerator
from b_logger.utils.formatters import format_tb
from b_logger.generators.report_gen import ReportGenerator


class RunTime:
    def __init__(self):
        self.run_report: Report = Report()
        self.test_report: TestReport = TestReport()
        self.step_manager = StepManager()
        self.step_container = StepContainer()
        self.report_generator: ReportGenerator = ReportGenerator()
        self.html_generator: HTMLGenerator = HTMLGenerator()

    def set_base_url(self, base_url: str):
        self.run_report.base_url = base_url

    def start_test(self, item):
        test_name = item.name
        # test_name = item.originalname

        self.step_manager = StepManager()
        self.step_container = StepContainer()

        self.test_report = TestReport(test_name)

        if hasattr(item, "callspec"):
            params = item.callspec.params
            for param_name, param_value in params.items():
                self.test_report.add_parameter(param_name, param_value)

    def set_test_status(self, status: TestStatus):
        self.test_report.set_status(status)

    def set_test_duration(self, duration: float):
        self.test_report.set_duration(duration)

    def set_test_error(self, error: TestError):
        self.test_report.error = error

    def finish_test(self):
        self.step_container.save_json()
        self.test_report.set_steps_id(self.step_container.container_id)

    def handle_failed_test(self, call, report):
        status = py_outcome_to_tstatus(report.outcome)
        self.set_test_status(status)
        self.set_test_error(TestError(call.excinfo.exconly(), report.longreprtext))

    def handle_skipped_test(self, call, report):
        status = py_outcome_to_tstatus(report.outcome)
        self.set_test_status(status)
        self.set_test_error(call.excinfo.value)

    def start_step(self, step: Step):
        if self.step_manager.current_step_id is not None:
            step.set_parent_id(self.step_manager.current_step_id)
        else:
            self.step_manager.set_current_step(step.id)
            self.step_container.add_step(step)

    @staticmethod
    def handle_step_result(step: Step, exc=None):
        if exc:
            step.set_status(StepStatus.FAILED)
            err = StepError(exc, format_tb(traceback.format_exc(4)))
            step.add_error(err)
            return
        step.set_status(StepStatus.PASSED)

    def finish_step(self, step: Step):
        if step.parent_id:
            parent_step = self.step_container.get_step_by_id(step.parent_id)
            parent_step.add_sub_step(step)
            return
        self.step_manager.current_step_id = step.parent_id

    def print_message(self, step: Step):
        parent_step = (self.step_container.get_step_by_id
                       (self.step_manager.current_step_id)
                       )
        parent_step.add_sub_step(step)

    def attach(self):
        pass
