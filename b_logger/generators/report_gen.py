import os
from glob import glob
from filelock import FileLock

from b_logger.entities.reports import RunReport
from b_logger.utils.paths import b_logs_path, clear_b_logs_tmp, b_logs_tmp_reports_path


class ReportGenerator:
    def __init__(self):
        self.combined = RunReport()

    def generate_combined_report(self):
        self.load_reports()
        self.combined.set_end_time()
        self.combined.count_duration()
        self.save()
        self.clear_locks()

    def load_reports(self):
        report_files = glob(f'{b_logs_tmp_reports_path()}/report_*.json')
        for rep in report_files:
            try:
                report = RunReport.from_json(rep)
                self.merge(report)
            except Exception as e:
                print(f"[ERROR] Failed to process {rep}: {e}")
                raise e

    def merge(self, report: RunReport):
        self._merge_proj_name(report)
        self._merge_env(report)
        self._merge_base_url(report)
        self._merge_start_time(report)
        self._merge_end_time(report)
        self._merge_report_ids(report)
        self._merge_run_results(report)
        self._merge_module_results(report)

    def save(self, filename='blog_report'):
        output_path = f'{b_logs_path()}/{filename}'
        with FileLock(f'{output_path}.lock'):
            self.combined.to_json_file(output_path)
        # print(f"[INFO] Combined report saved to {output_path}")

    @staticmethod
    def clear_locks():
        for each in os.listdir(f'{b_logs_path()}'):
            if '.lock' in each:
                os.remove(f'{b_logs_path()}/{each}')

    def _merge_proj_name(self, report: RunReport):
        if self.combined.proj_name and self.combined.proj_name != report.proj_name:
            print(f"[WARN] Inconsistent project name: {self.combined.proj_name} vs {report.proj_name}")

        self.combined.proj_name = report.proj_name

    def _merge_env(self, report: RunReport):
        if self.combined.env and self.combined.env != report.env:
            print(f"[WARN] Inconsistent env: {self.combined.env} vs {report.env}")

        self.combined.env = report.env

    def _merge_base_url(self, report: RunReport):
        if self.combined.base_url and self.combined.base_url != report.base_url:
            print(f"[WARN] Inconsistent base url: {self.combined.base_url} vs {report.base_url}")

        self.combined.base_url = report.base_url

    def _merge_start_time(self, report: RunReport):
        if report.start_time and (
            self.combined.start_time is None or report.get_iso_start_time() < self.combined.get_iso_start_time()
        ):
            self.combined.start_time = report.start_time

    def _merge_end_time(self, report: RunReport):
        if report.end_time and (
            self.combined.end_time is None or report.get_iso_end_time() > self.combined.get_iso_end_time()
        ):
            self.combined.end_time = report.end_time

    def _merge_report_ids(self, report: RunReport):
        self.combined.report_ids[report.worker] = report.report_id

    def _merge_run_results(self, report: RunReport):
        for status, count in report.run_results.items():
            self.combined.run_results.increase(status, count)
            # self.combined.run_results[status] += count

    def _merge_module_results(self, report: RunReport):
        self.combined.combine_modules_from_report(report)
