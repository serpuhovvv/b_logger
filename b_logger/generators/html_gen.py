import json
from jinja2 import Environment, FileSystemLoader

from b_logger.entities.reports import RunReport
from b_logger.utils.paths import pathfinder, b_logs_path


class HTMLGenerator:
    def __init__(self):
        env = Environment(loader=FileSystemLoader(f'{pathfinder.library_root()}/b_logger/templates'))
        self.template = env.get_template(f'base_template.html')
        self.summary_template = env.get_template(f'summary_template.html')
        self.report_path = f'{b_logs_path()}/blog_report.json'

    def generate_html(self):
        combined_report = RunReport.from_json(self.report_path)

        try:
            steps = combined_report.get_steps()

            html = self.template.render(
                report=combined_report,
                steps=steps
            )

            with open(f'{b_logs_path()}/blog_report.html', 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            raise RuntimeError(f'blog_report.html generation failed: {e}')

        try:
            html_summary = self.summary_template.render(
                report=combined_report
            )

            with open(f'{b_logs_path()}/blog_summary.html', 'w', encoding='utf-8') as f:
                f.write(html_summary)
        except Exception as e:
            raise RuntimeError(f'blog_summary.html generation failed: {e}')
