import json
import os
import traceback
from pathlib import Path
from typing import Union, BinaryIO

from b_logger.entities.reports import RunReport
from b_logger.entities.tests import TestReport, TestStatus
from b_logger.entities.attachments import Attachment
from b_logger.entities.prints import Print
from b_logger.entities.steps import Step, StepStatus, StepError, StepContainer
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.integrations import Integrations
from b_logger.utils.browser_adapters import get_browser_adapter
from b_logger.utils.formatters import format_tb
from b_logger.utils.paths import attachments_path


class TestRun:
    pass


class RunTime:
    def __init__(self):
        self.run_report: RunReport = RunReport()
        self.browser: "RemoteWebDriver | WebDriver | Page | None" = None
        self.test_report: TestReport = TestReport()
        self.step_container: StepContainer = StepContainer()

    def set_base_url(self, base_url: str):
        self.run_report.set_base_url(base_url)

    def set_env(self, env: str):
        self.run_report.set_env(env)

    def set_browser(self, browser: "RemoteWebDriver | WebDriver | Page"):
        self.browser = browser

    def start_test(self, item):
        module = item.location[0]
        test_name = item.name
        test_originalname = item.originalname

        self.step_container = StepContainer()
        self.test_report = TestReport(module, test_name, test_originalname)

    def finish_test(self):
        self.step_container.save_json()
        self.test_report.set_steps(self.step_container.container_id)

        self.run_report.add_result(self.test_report)

        del self.step_container, self.test_report
        if self.browser:
            self.browser = None

    def process_test_result(self, report, call, item):
        """Process test results and set appropriate status."""

        self.test_report.set_duration(round(report.duration, 2))

        if report.longrepr:
            self.test_report.set_stacktrace(report.longreprtext)

        if report.failed:
            self._handle_failed_test(call, report, item)

        elif report.skipped:
            self._handle_skipped_test(call, report, item)

        else:
            self._handle_passed_test(call, report, item)

    def _handle_failed_test(self, call, report, item):
        self.make_screenshot(is_error=True)
        self.test_report.set_error(call.excinfo.exconly())

    def _handle_skipped_test(self, call, report, item):
        self.make_screenshot(is_error=True)
        self.test_report.set_error(call.excinfo.exconly())

    def _handle_passed_test(self, call, report, item):
        pass

    def process_test_status(self, report, call, item):
        if hasattr(report, 'wasxfail'):
            if report.outcome == 'skipped':
                status = TestStatus.PASSED
            else:
                status = TestStatus.FAILED
        else:
            if call.excinfo:
                if call.excinfo.typename == "AssertionError":
                    status = TestStatus.FAILED
                else:
                    status = TestStatus.BROKEN
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

            if step.parent_id is None:
                self.step_container.failed = False

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

    def apply_info(self, **kwargs):

        if not kwargs:
            print('[BLogger][WARN] blog.info() requires at least one keyword argument')
            return

        info = {}

        for k, v in kwargs.items():
            key = k.replace('_', ' ').capitalize().upper()

            info[key] = v

            # Integrations.info(key, v)

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

    def print_message(self, message):
        if isinstance(message, (dict, list)):
            data = json.dumps(message, indent=2, ensure_ascii=False)
        else:
            data = str(message)

        print_ = Print(data)

        current_step = self.step_container.get_current_step()

        if current_step:
            print_.set_parent_id(current_step.id)
            current_step.add_sub_step(print_)
        else:
            self.step_container.add_step(print_)

        print(f'{data}')

    def make_screenshot(self, scr_name: str = None, is_error: bool = False):
        if self.browser is None:
            return

        scr_name = (f'{"err_" if is_error else ""}'
                    f'scr_'
                    f'{self.test_report.name if not scr_name else scr_name}')

        adapter = get_browser_adapter(self.browser)

        try:
            screenshot_bytes = adapter.make_screenshot()
            self.attach(screenshot_bytes, scr_name)
        except Exception as e:
            print(f'[BLogger][ERROR] Unable to make screenshot: {e}')

    def attach(self,
               source: Union[str, Path, bytes, BinaryIO, dict, list, int, float, None],
               name: str = None,
               mime_type: str = None
               ):
        if name:
            existing_names = {Path(att.name).stem for att in self.test_report.attachments}
            base_name = name
            index = 0
            while name in existing_names:
                index += 1
                name = f'{base_name}_{index}'

        attachment = Attachment(source=source, name=name)

        current_step = self.step_container.get_current_step()
        if current_step:
            current_step.add_attachment(attachment)

        self.test_report.add_attachment(attachment)

        Integrations.attach(source, attachment)

    # def link(self, id_):
    #     if blog_config.link_prefix:
    #         url = f'{blog_config.link_prefix}/{id_}'
    #     else:
    #         url = f'{id_}'
    #
    #     self.apply_info(link=url)
    #
    #     Integrations.link(url)
