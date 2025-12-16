"""
Copyright 2025 Serg Pudikov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import traceback
from pathlib import Path
from typing import Union, BinaryIO, Optional, Any

from b_logger.entities.reports import RunReport
from b_logger.entities.tests import TestReport, TestStatus
from b_logger.entities.attachments import Attachment
from b_logger.entities.prints import Print
from b_logger.entities.steps import Step, StepStatus, StepError, StepContainer
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.integrations import Integrations
from b_logger.utils.browser_adapters import get_browser_adapter
from b_logger.utils.json_handler import process_json


class RunTime:
    def __init__(self):
        self.run_report: RunReport = RunReport()
        self.browser: "RemoteWebDriver | WebDriver | Page | None" = None
        self.test_report: TestReport = TestReport()
        self.step_container: StepContainer = StepContainer()

    def set_env(self, env: str):
        self.run_report.set_env(env)

    def set_base_url(self, base_url: str):
        self.run_report.set_base_url(base_url)

    def set_browser(self, browser: "RemoteWebDriver | WebDriver | Page"):
        self.browser = browser

    def start_test(self, item):
        module = item.location[0]
        test_name = item.name
        test_originalname = item.originalname

        self.test_report = TestReport(module, test_name, test_originalname)
        self.step_container = StepContainer()

    def finish_test(self):
        self.step_container.save_json()
        self.test_report.add_steps(self.step_container.container_id)

        self.run_report.add_test_report(self.test_report)

        del self.test_report, self.step_container

        if self.browser:
            self.browser = None

    def start_retry(self):
        self.test_report.description = None
        self.test_report.info = {}
        self.test_report.known_bugs = []

        self.step_container.save_json()
        self.test_report.add_steps(self.step_container.container_id)

        self.step_container = StepContainer()

    def process_test_result(self, report, call, item):
        """Process test results and set appropriate status."""

        self.test_report.set_duration(round(report.duration, 2))

        if report.longrepr:
            self.test_report.set_stacktrace(report.longreprtext)

        if self._was_xfail(report):
            self._handle_xfail(report, call, item)
            return

        if report.failed:
            self._handle_failed_test(call, report, item)

        elif report.skipped:
            self._handle_skipped_test(call, report, item)

        else:
            self._handle_passed_test(call, report, item)

    def _handle_failed_test(self, call, report, item):
        self.make_screenshot(is_error=True)
        self._process_exc_info(call)

    def _handle_skipped_test(self, call, report, item):
        self._process_exc_info(call)

    def _handle_passed_test(self, call, report, item):
        pass

    def _process_exc_info(self, call):
        if call.excinfo:
            self.test_report.set_error(call.excinfo.exconly())

    @staticmethod
    def _was_xfail(report):
        if getattr(report, 'wasxfail', None) or hasattr(report, 'wasxfail') or ('XPASS' in report.longreprtext):
            return True
        return False

    def _handle_xfail(self, report, call, item):
        if report.outcome == 'skipped':
            self.make_screenshot(f'xfail_{self.test_report.name}')

            if call.excinfo:
                msg = f'XFAIL: {getattr(report, 'wasxfail', None) or "test failed as expected"}\n\n'
                self.test_report.set_error(msg + call.excinfo.exconly())
            else:
                msg = f'XFAIL: {getattr(report, 'wasxfail', None) or "test failed as expected"}'
                self.test_report.set_error(msg)

        elif report.outcome == 'failed':
            msg = f'XPASS: {getattr(report, 'wasxfail', None) or "test passed, but was marked xfail"}'
            self.test_report.set_error(msg)

        elif report.outcome == 'passed':
            msg = f'XPASS: {getattr(report, 'wasxfail', None) or "test passed, but was marked xfail"}'
            self.test_report.set_error(msg)

    def process_test_status(self, report, call, item):
        if self._was_xfail(report):
            status = py_outcome_to_tstatus(report.outcome)
        else:
            if report.outcome == 'failed' and call.excinfo:
                if call.excinfo.typename == 'AssertionError':
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
                self.make_step_err_scr(step)

                step.set_error(StepError(exc, traceback.format_exc(4)))

                self.step_container.failed = True

            if not step.parent_id:
                self.step_container.failed = False

            step.set_status(StepStatus.FAILED)

            return

        step.set_status(StepStatus.PASSED)

    def finish_step(self, step: Step):
        step.count_duration()
        self.step_container.set_current_step(step.parent_id)

    def apply_description(self, description: str):
        if not self.test_report.description:
            self.test_report.set_description(description)
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

            Integrations.info(k, v)

        current_step = self.step_container.get_current_step()

        if current_step:
            current_step.add_info(info)

        self.test_report.add_info(info)

    def apply_link(self, **kwargs):

        links = {}

        for k, v in kwargs.items():
            key = k.replace('_', ' ').capitalize().upper()

            links[key] = f'<a href={v}>{v}</a>'

            Integrations.link(v, key)

        current_step = self.step_container.get_current_step()

        if current_step:
            current_step.add_links(links)

        self.test_report.add_links(links)

    def apply_known_bug(self, url: Optional[str] = None, description: Optional[str] = None):
        if not url and not description:
            print('[BLogger][WARN] blog.known_bug() requires at least url or description')
            return

        bug = {
            "url": url,
            "description": description
        }

        current_step = self.step_container.get_current_step()

        if current_step:
            current_step.add_known_bug(bug)

        self.test_report.add_known_bug(bug)

    def print_message(self, message: Any):
        if isinstance(message, (dict, list)):
            data = process_json(message)
            type_ = 'application/json'
        else:
            data = str(message)
            type_ = 'text/plain'

        print_ = Print(data)

        current_step = self.step_container.get_current_step()

        if current_step:
            print_.set_parent_id(current_step.id)
            current_step.add_sub_step(print_)
        else:
            self.step_container.add_step(print_)

        print(f'{data}')

        Integrations.attach(data, print_.id, type_)

    def make_screenshot(self, scr_name: Optional[str] = None, is_error: bool = False):
        if self.browser is None:
            return

        scr_name = (
            f'{"err_" if is_error else ""}'
            f'scr_{self.test_report.name if not scr_name else scr_name}.png'
        )

        adapter = get_browser_adapter(self.browser)

        try:
            screenshot_bytes = adapter.make_screenshot()

            if screenshot_bytes:
                if isinstance(screenshot_bytes, list):
                    for scr in screenshot_bytes:
                        self.attach(scr, scr_name)
                else:
                    self.attach(screenshot_bytes, scr_name)
        except Exception as e:
            print(f'[BLogger][ERROR] Unable to make screenshot: {e}')

    def make_step_err_scr(self, step: Step):
        if self.browser is None:
            return

        adapter = get_browser_adapter(self.browser)

        try:
            screenshot_bytes = adapter.make_screenshot()

            if screenshot_bytes:
                if isinstance(screenshot_bytes, list):
                    for scr in screenshot_bytes:
                        step.add_attachment(Attachment(scr))
                else:
                    step.add_attachment(Attachment(screenshot_bytes))
        except Exception as e:
            print(f'[BLogger][ERROR] Unable to make step error screenshot for step {step.title}: {e}')

    def attach(self, content: Union[bytes, Path, BinaryIO, str, dict, list, int, float, bool, None], name: Optional[str] = None):

        attachment = Attachment(content=content, name=name)

        current_step = self.step_container.get_current_step()
        if current_step:
            current_step.add_attachment(attachment)

        self.test_report.add_attachment(attachment)

        if name not in ['stdout', 'stderr', 'log']:
            Integrations.attach(content, attachment.name, attachment.type_)

    def apply_integrations(self):
        d = self.test_report.description
        if d:
            Integrations.description(d)

        i = self.test_report.info
        if i:
            Integrations.attach(process_json(i), 'blog_info', 'text/html')

        kb = self.test_report.known_bugs
        if kb:
            Integrations.attach(process_json(kb), 'blog_known_bugs', 'text/html')
