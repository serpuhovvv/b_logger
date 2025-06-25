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
        self.base_url = None
        self.env = None
        self.worker = None
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.report_ids = {}
        self.run_results = RunResults()
        self.modules: dict[str, dict] = defaultdict(
            lambda: {
                "results": RunResults(),
                "tests": defaultdict(list)
            }
        )

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def set_env(self, env: str):
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

    def add_result(self, test_report: TestReport):
        module = test_report.module
        test_name = test_report.originalname
        status = test_report.status

        self.modules[module]['tests'][test_name].append(test_report)

        self.modules[module]['results'].increase(status)
        self.run_results.increase(status)

    def get_steps(self) -> dict:
        steps_by_id = {}
        if self.modules:
            for module_data in self.modules.values():
                for test_name, test_reports in module_data["tests"].items():
                    for report in test_reports:
                        steps_id = report.get('steps')
                        if steps_id:
                            path = f'{b_logs_tmp_steps_path()}/{steps_id}.json'
                            try:
                                steps_by_id[steps_id] = StepContainer.from_json(path)
                            except FileNotFoundError:
                                continue
        return steps_by_id

    def combine_modules(self, run_report):
        if run_report.modules:
            for module_name, module_data in run_report.modules.items():
                mod_results = module_data["results"]
                mod_tests: dict = module_data["tests"]

                module = self.modules[module_name]

                for status, count in mod_results.items():
                    module['results'].increase(status, count)

                for test_name, test_reports in mod_tests.items():
                    module['tests'][test_name].extend(test_reports)

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
