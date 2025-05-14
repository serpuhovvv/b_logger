import json
from jinja2 import Environment, FileSystemLoader

from b_logger.entities.reports import Report
from b_logger.utils.paths import pathfinder, logs_path


class HTMLGenerator:
    def __init__(self):
        env = Environment(loader=FileSystemLoader(f'{pathfinder.library_root()}/b_logger/templates'))
        self.template = env.get_template(f'adm_template.html')
        self.report_path = f'{logs_path()}/combined_report.json'

    def load_report(self):
        return Report.from_json(self.report_path)

    def generate_html(self):
        combined_report = self.load_report()

        steps_by_test = combined_report.get_steps_by_test()

        html = self.template.render(report=combined_report, steps_by_test=steps_by_test)
        with open(f'{logs_path()}/report_sum.html', 'w', encoding='utf-8') as f:
            f.write(html)
