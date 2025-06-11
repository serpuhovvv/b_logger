import json
import os
import traceback
from pathlib import Path
from typing import Union, BinaryIO

from playwright.sync_api import Page
from selenium.webdriver.ie.webdriver import RemoteWebDriver, WebDriver

from b_logger.entities.attachments import Attachment
from b_logger.entities.prints import Print, PrintStatus
from b_logger.entities.reports import RunReport
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.entities.tests import TestReport, TestStatus
from b_logger.entities.steps import Step, StepStatus, StepError, StepContainer
from b_logger.integrations import Integrations
from b_logger.utils.formatters import format_tb
from b_logger.utils.paths import attachments_path


class TestRun:
    pass


class RunTime:
    def __init__(self):
        self.run_report: RunReport = RunReport()
        self.browser: RemoteWebDriver | WebDriver | Page | None = None
        self.test_report: TestReport = TestReport()
        self.step_container: StepContainer = StepContainer()

    def set_base_url(self, base_url: str):
        self.run_report.base_url = base_url

    def set_env(self, env: str):
        self.run_report.set_env(env)

    def set_browser(self, browser: RemoteWebDriver | WebDriver | Page):
        self.browser = browser

    def start_test(self, item):
        test_name = item.name
        # test_name = item.originalname

        self.step_container = StepContainer()
        self.test_report = TestReport(test_name)

    def finish_test(self):
        self.step_container.save_json()
        self.test_report.set_steps(self.step_container.container_id)

        del self.step_container, self.test_report
        if self.browser:
            self.browser = None

    def process_test_result(self, report, call, item):
        """Process test results and set appropriate status."""

        self.test_report.set_duration(round(report.duration, 2))

        if report.longrepr:
            self.test_report.set_stacktrace(report.longreprtext)

        if report.failed:
            # self.make_screenshot(is_error=True)
            self._handle_failed_test(call, report, item)

        elif report.skipped:
            # self.make_screenshot(is_error=True)
            self._handle_skipped_test(call, report, item)

        else:
            self._handle_passed_test(call, report, item)

    def _handle_failed_test(self, call, report, item):
        self.test_report.set_error(call.excinfo.exconly())

    def _handle_skipped_test(self, call, report, item):
        self.test_report.set_error(call.excinfo.exconly())

    def _handle_passed_test(self, call, report, item):
        pass

    def process_test_status(self, report):
        if hasattr(report, 'wasxfail'):
            if report.outcome == 'skipped':
                status = TestStatus.PASSED
            elif report.outcome in ['passed', 'failed']:
                status = TestStatus.FAILED
            else:
                status = py_outcome_to_tstatus(report.outcome)
        else:
            status = py_outcome_to_tstatus(report.outcome)

        self.test_report.set_status(status)

        return status

    def start_step(self, step: Step):
        if self.step_container.current_step_id is not None:
            parent = self.step_container.get_current_step()
            step.set_parent_id(parent.id)

            parent.add_sub_step(step)

            self.step_container.set_current_step(step.id)

        else:
            self.step_container.set_current_step(step.id)
            self.step_container.add_step(step)

    def handle_step_result(self, step: Step, exc=None):
        if exc:
            if not self.step_container.failed:
                self.make_screenshot(is_error=True)

                step.set_error(StepError(exc, format_tb(traceback.format_exc(4))))

                self.step_container.failed = True

            step.set_status(StepStatus.FAILED)

            return

        step.set_status(StepStatus.PASSED)

    def finish_step(self, step: Step):
        self.step_container.set_current_step(step.parent_id)

    def apply_description(self, description):
        if not self.test_report.description:
            self.test_report.set_description(description)
            Integrations.description(description)
        else:
            self.test_report.modify_description(description)

    def apply_param(self, name, value):
        self.test_report.add_parameter(name, value)

    def apply_info(self, **kwargs):

        if not kwargs:
            raise ValueError('blog.info() requires at least one keyword argument')

        info = {}

        for k, v in kwargs.items():
            key = k.replace('_', ' ').capitalize()

            info[key] = v

        current_step = self.step_container.get_current_step()

        if current_step:
            current_step.add_info(info)
        else:
            self.test_report.add_info(info)

    def apply_known_bug(self, description: str, url: str = None):
        bug = {"description": description, "url": url}

        current_step = self.step_container.get_current_step()

        if current_step:
            current_step.add_known_bug(bug)

        self.test_report.add_known_bug(bug)

    def print_message(self, message, status: PrintStatus = PrintStatus.NONE):
        if isinstance(message, (dict, list)):
            data = json.dumps(message, indent=2, ensure_ascii=False)
        else:
            data = str(message)

        print_ = Print(data, status)

        current_step = self.step_container.get_current_step()

        if current_step:
            print_.set_parent_id(current_step.id)
            current_step.add_sub_step(print_)
        else:
            self.step_container.add_step(print_)

        print(f'\n{data}')

    def make_screenshot(self, scr_name: str = None, is_error: bool = False):
        if self.browser is None:
            return

        if not scr_name:
            index = 1
            while True:
                if is_error:
                    scr_name = f'err_scr_{self.test_report.name}_{index}.png'
                else:
                    scr_name = f'scr_{self.test_report.name}_{index}.png'

                if scr_name not in os.listdir(attachments_path()):
                    break
                index += 1

        if isinstance(self.browser, (RemoteWebDriver, WebDriver)):
            try:
                self.attach(self.browser.get_screenshot_as_png(), scr_name)
            except Exception as e:
                raise RuntimeError(f'Unable to make screenshot: {e}')

        elif isinstance(self.browser, Page):
            pages = self.browser.context.pages
            for page in pages:
                try:
                    self.attach(page.screenshot(), scr_name)
                    return
                except Exception as e:
                    pass

            raise RuntimeError(f'Unable to make screenshot! There is no valid playwright page: {pages}')

        else:
            raise RuntimeError(f'Browser is incorrect, unable to make screenshot!!! '
                               f'Current browser is {self.browser}')

    def attach(self, source: Union[str, Path, bytes, BinaryIO], name: str = None, mime_type: str = None):
        attachment = Attachment(source, name)

        current_step = self.step_container.get_current_step()
        if current_step:
            current_step.add_attachment(attachment)

        self.test_report.add_attachment(attachment)

        Integrations.attach(source, attachment)
