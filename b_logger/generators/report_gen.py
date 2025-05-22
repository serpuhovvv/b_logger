import os
from glob import glob
from filelock import FileLock
# from box import Box

from b_logger.entities.reports import RunReport
from b_logger.utils.paths import b_logs_path, b_logs_tmp_path, clear_b_logs_tmp, b_logs_tmp_reports_path


class ReportGenerator:
    def __init__(self, debug=True):
        self.combined = RunReport()
        self.debug = debug

    def generate_combined_report(self):
        self.load_reports()
        self.combined.set_end_time()
        self.combined.count_duration()
        self.save()
        self.clear_locks()
        self.clear_tmp_dir()

    def load_reports(self):
        report_files = glob(f'{b_logs_tmp_reports_path()}/report_*.json')
        for rep in report_files:
            try:
                report = RunReport.from_json(rep)
                self.merge(report)
            except Exception as e:
                print(f"[ERROR] Failed to process {rep}: {e}")
                raise e
            # finally:
            #     os.remove(f'{path}')

    def merge(self, report: RunReport):
        self._merge_env(report)
        self._merge_proj_name(report)
        self._merge_base_url(report)
        self._merge_start_time(report)
        self._merge_end_time(report)
        self._merge_report_ids(report)
        self._merge_run_results(report)
        self._merge_module_results(report)

    def save(self, filename='combined_report'):
        output_path = f'{b_logs_path()}/{filename}'
        with FileLock(f'{output_path}.lock'):
            self.combined.to_json_file(output_path)
        # print(f"[INFO] Combined report saved to {output_path}")

    @staticmethod
    def clear_locks():
        # lock_files = glob(f"{logs_path()}/report_*.json.lock")
        for lock_file in os.listdir(f'{b_logs_path()}'):
            if '.lock' in lock_file:
                os.remove(f'{b_logs_path()}/{lock_file}')

    def clear_tmp_dir(self):
        if not self.debug:
            clear_b_logs_tmp(rmdir=True)

    def _merge_proj_name(self, report: RunReport):
        if self.combined.proj_name is None:
            self.combined.proj_name = report.proj_name
        elif self.combined.proj_name != report.proj_name:
            print(f"[WARN] Inconsistent project name: {self.combined.proj_name} vs {report.proj_name}")

    def _merge_env(self, report: RunReport):
        if self.combined.env is None:
            self.combined.env = report.env
        elif self.combined.env != report.env:
            print(f"[WARN] Inconsistent env: {self.combined.env} vs {report.env}")

    def _merge_base_url(self, report: RunReport):
        if self.combined.base_url is None:
            self.combined.base_url = report.base_url
        elif self.combined.base_url != report.base_url:
            print(f"[WARN] Inconsistent base url: {self.combined.base_url} vs {report.base_url}")

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
        for module_name, module_data in report.modules.items():
            mod_results = module_data['module_results']
            mod_tests = module_data['module_tests']
            # self.combined.add_test_report(module_name)

            mod_combined = self.combined.modules[module_name]

            for status, count in mod_results.items():
                mod_combined['module_results'][status] += count

            for test_name, test_data in mod_tests.items():
                mod_combined['module_tests'][test_name] = test_data

            # mod_combined["tests"].extend(mod_data.get("tests", []))


# class ReportGenerator:
#     def __init__(self):
#         self.combined = {
#             "proj_name": None,
#             "env": None,
#             "start_time": None,
#             "report_ids": [],
#             "run_results": defaultdict(int),
#             "module_results": defaultdict(lambda: {
#                 "passed": 0,
#                 "failed": 0,
#                 "skipped": 0,
#                 "broken": 0,
#                 "tests": []
#             })
#         }
#
#     def generate_combined_report(self):
#         self.load_reports()
#         self.save()
#
#     def load_reports(self):
#         report_files = glob(f"{logs_path()}/report_*.json")
#
#         for each in report_files:
#             with open(each, "r", encoding="utf-8") as file:
#                 try:
#                     report = json.load(file)
#                     self.merge(report)
#                 except json.JSONDecodeError as e:
#                     print(f"[ERROR] Failed to load {each}: {e}")
#
#     def merge(self, report):
#         self._merge_env(report)
#         self._merge_proj_name(report)
#         self._merge_start_time(report)
#         self._merge_report_id(report)
#         self._merge_run_results(report)
#         self._merge_module_results(report)
#
#     def save(self, filename="combined_report.json"):
#         output_path = f'{logs_path()}/{filename}'
#         with FileLock(f'{output_path}.lock'):
#             with open(output_path, "w", encoding="utf-8") as file:
#                 json.dump(self.combined, file, indent=4)
#             print(f"[INFO] Combined report saved to {output_path}")
#
#     def _merge_env(self, report):
#         if self.combined["env"] is None:
#             self.combined["env"] = report["env"]
#         elif self.combined["env"] != report["env"]:
#             print(f"[WARN] Inconsistent env: {self.combined['env']} vs {report['env']}")
#
#     def _merge_proj_name(self, report):
#         if self.combined["proj_name"] is None:
#             self.combined["proj_name"] = report["proj_name"]
#         elif self.combined["proj_name"] != report["proj_name"]:
#             print(f"[WARN] Inconsistent project name: {self.combined['proj_name']} vs {report['proj_name']}")
#
#     def _merge_start_time(self, report):
#         try:
#             report_start = datetime.fromisoformat(report["start_time"])
#             if self.combined["start_time"] is None or report_start < datetime.fromisoformat(self.combined["start_time"]):
#                 self.combined["start_time"] = report["start_time"]
#         except Exception as e:
#             print(f"[WARN] Could not parse start_time: {e}")
#
#     def _merge_report_id(self, report):
#         self.combined["report_ids"].append(report["report_id"])
#
#     def _merge_run_results(self, report):
#         for status, count in report.get("run_results", {}).items():
#             self.combined["run_results"][status] += count
#
#     def _merge_module_results(self, report):
#         for module, mod_data in report.get("module_results", {}).items():
#             mod_combined = self.combined["module_results"][module]
#             for status in ["passed", "failed", "skipped", "broken"]:
#                 mod_combined[status] += mod_data.get(status, 0)
#             mod_combined["tests"].extend(mod_data.get("tests", []))
#
    # def _finalize(self):
    #     # Преобразуем defaultdict в обычный dict для сохранения
    #     result = self.combined.copy()
    #     result["run_results"] = dict(result["run_results"])
    #     result["module_results"] = dict(result["module_results"])
    #     return result
