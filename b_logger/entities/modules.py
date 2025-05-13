# import uuid
# from filelock import FileLock
#
# from b_logger import tmp_logs_path
# from b_logger.utils.basedatamodel import BaseDataModel
# from b_logger.entities.statuses import TestStatus
# from b_logger.entities.tests import TestReport
#
#
# class ModuleTestResults(BaseDataModel):
#     def __init__(self):
#         self.passed: int = 0
#         self.failed: int = 0
#         self.broken: int = 0
#         self.skipped: int = 0
#
#     def increase(self, result: TestStatus):
#         if not hasattr(self, result):
#             raise ValueError(f'Unsupported test status: {result}')
#         current = getattr(self, result)
#         setattr(self, result, current + 1)
#
#
# class ModuleTestReports(BaseDataModel, list):
#     def __init__(self):
#         super().__init__()
#
#     def add_test_report(self, test_report: TestReport):
#         self.append(test_report)
#
#     def get_test_report_by_id(self, test_rep_id):
#         for rep in self:
#             if rep.id == test_rep_id:
#                 return rep
#             else:
#                 raise ValueError(f'No such test run_report id: {test_rep_id}')
#
#
# class ModuleData(BaseDataModel):
#     def __init__(self, module_name):
#         self.module_id = f'modules_{uuid.uuid4()}'
#         self.module_name = module_name
#         self.module_results = ModuleTestResults()
#         self.module_tests = ModuleTestReports()
#
#     def add_module_result(self, result: TestStatus):
#         self.module_results.increase(result)
#
#     def add_test_report(self, test_report: TestReport):
#         test_name = test_report.name
#         self.module_tests[test_name] = test_report
#
#     def save_json(self, file_name=None):
#         root = f'{tmp_logs_path()}/modules'
#         if file_name:
#             path = f'{root}/{file_name}'
#         else:
#             path = f'{root}/{self.module_id}'
#         with FileLock(f'{path}.lock'):
#             self.to_json_file(path)
#
#
# class ModuleDataContainer(BaseDataModel, dict):
#     def __init__(self, module_name):
#         super().__init__()
#
#     def add_module(self, module_data: ModuleData):
#         self[module_data.module_name] = module_data.module_id
#