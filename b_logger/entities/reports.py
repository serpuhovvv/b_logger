import os
import json
import uuid
from collections import defaultdict
from datetime import datetime
from dateutil import parser
from filelock import FileLock

from b_logger.config import blog_config
from b_logger.entities.statuses import TestStatus
from b_logger.entities.tests import TestReport
from b_logger.entities.steps import StepContainer
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import b_logs_path, b_logs_tmp_path, b_logs_tmp_steps_path, b_logs_tmp_reports_path


class RunResults(BaseDataModel):
    def __init__(self):
        self.PASSED: int = 0
        self.FAILED: int = 0
        self.BROKEN: int = 0
        self.SKIPPED: int = 0

    def increase(self, result: TestStatus, amount: int = 1):
        if not hasattr(self, result):
            raise ValueError(f'Unsupported test status: {result}')
        current = getattr(self, result)
        setattr(self, result, current + amount)


class RunReport(BaseDataModel):
    def __init__(self):
        self.report_id = f'report_{uuid.uuid4()}'
        self.proj_name = blog_config.project_name
        self.env = None
        self.base_url = None
        self.worker = None
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.report_ids = {}
        # self.run_results = {TestStatus.PASSED: 0,
        #                     TestStatus.FAILED: 0,
        #                     TestStatus.BROKEN: 0,
        #                     TestStatus.SKIPPED: 0
        #                     }
        self.run_results = RunResults()
        self.modules = defaultdict(
            lambda: {
                "module_results": {
                    TestStatus.PASSED: 0,
                    TestStatus.FAILED: 0,
                    TestStatus.BROKEN: 0,
                    TestStatus.SKIPPED: 0
                },
                "module_tests": {}
            }
        )

    def set_env(self, env):
        self.env = env

    def set_worker(self, worker):
        self.worker = worker

    def set_end_time(self):
        self.end_time = datetime.now()

    def count_duration(self):
        if isinstance(self.start_time, str) or isinstance(self.end_time, str):
            self.start_time = self.get_iso_start_time()
            self.end_time = self.get_iso_end_time()

        self.duration = self.end_time - self.start_time

    def get_iso_start_time(self):
        if isinstance(self.start_time, str):
            self.start_time = parser.parse(self.start_time)
        return self.start_time

    def get_iso_end_time(self):
        if isinstance(self.end_time, str):
            self.end_time = parser.parse(self.end_time)
        return self.end_time

    def add_run_result(self, result):
        self.run_results.increase(result)

    def add_module_result(self, module, result):
        self.modules[module]['module_results'][result] += 1

    def add_test_report(self, module: str, test_report: TestReport):
        test_name = test_report.name

        # test_exists = self.modules[module]['module_tests'].get(test_name, {})
        #
        # if test_exists:
        #     self.modules[module]['module_tests'][test_name] = [self.modules[module]['module_tests'][test_name]]
        #     self.modules[module]['module_tests'][test_name].append(test_report)
        # else:
        self.modules[module]['module_tests'][test_name] = test_report

    def get_steps_by_test(self):
        steps_by_test = {}
        for module_tests in self._get_module_tests().values():
            for test_name, test_data in module_tests.items():
                steps_id = test_data.get('steps')
                if steps_id:
                    steps_path = f'{b_logs_tmp_steps_path()}/{steps_id}.json'
                    try:
                        steps_by_test[test_name] = StepContainer.from_json(steps_path)
                    except FileNotFoundError:
                        pass

        # if test_name:
        #     return steps_by_test.get(test_name, {})

        return steps_by_test

    def _get_module_tests(self):
        module_tests = {}
        for module_name, module_data in self.modules.items():
            tests = dict(module_data['module_tests'])
            module_tests[module_name] = tests

        # if module_name:
        #     return module_tests.get(module_name, {})

        return module_tests

    def combine(self):
        pass

    def save_json(self, file_name=None):
        root = f'{b_logs_tmp_reports_path()}'
        if file_name:
            path = f'{root}/{file_name}'
        else:
            path = f'{root}/{self.report_id}'
        with FileLock(f'{path}.lock'):
            self.to_json_file(path)

    # def get_modules(self):
    #     return self.modules.keys()
