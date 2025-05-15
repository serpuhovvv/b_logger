import traceback

from playwright.sync_api import Page
from selenium.webdriver.ie.webdriver import WebDriver

from b_logger.entities.reports import RunReport
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.entities.tests import TestReport, TestStatus, TestError
from b_logger.entities.steps import Step, StepStatus, StepError, StepManager, StepContainer
from b_logger.generators.html_gen import HTMLGenerator
from b_logger.utils.formatters import format_tb
from b_logger.generators.report_gen import ReportGenerator
from b_logger.utils.paths import pathfinder, attachments_path, screenshots_path


class RunTime:
    def __init__(self):
        self.run_report: RunReport = RunReport()
        self.browser: WebDriver | Page = None
        self.test_report: TestReport = None
        self.step_manager: StepManager = None
        self.step_container: StepContainer = None

    def set_base_url(self, base_url: str):
        self.run_report.base_url = base_url

    def set_env(self, env: str):
        self.run_report.set_env(env)

    def set_browser(self, browser: WebDriver | Page):
        self.browser = browser

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

    def finish_test(self):
        self.step_container.save_json()
        self.test_report.set_steps_id(self.step_container.container_id)

    def handle_failed_test(self, call, report):
        status = py_outcome_to_tstatus(report.outcome)
        self.test_report.set_status(status)

        self.test_report.set_error(TestError(call.excinfo.exconly(), report.longreprtext))

    def handle_skipped_test(self, call, report):
        status = py_outcome_to_tstatus(report.outcome)
        self.test_report.set_status(status)

        self.test_report.set_error(TestError(call.excinfo.exconly(), report.longreprtext))

    def start_step(self, step: Step):
        if self.step_manager.current_step_id is not None:
            step.set_parent_id(self.step_manager.current_step_id)
        else:
            self.step_manager.set_current_step(step.id)
            self.step_container.add_step(step)

    def handle_step_result(self, step: Step, exc=None):
        if exc:
            self.make_screenshot(f'{self.test_report.name}_error')

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

    def make_screenshot(self, scr_name: str = None, is_error: bool = False):
        if self.browser is None:
            return

        scr_path = f'{screenshots_path()}/{scr_name}.png'

        if isinstance(self.browser, WebDriver):
            self.browser.save_screenshot(filename=scr_path)

        elif isinstance(self.browser, Page):
            self.browser.screenshot(path=scr_path)

        else:
            raise RuntimeError(f'Browser is incorrect, unable to make screenshot!!!'
                               f'Current browser is {self.browser}')

    def attach(self):
        pass
