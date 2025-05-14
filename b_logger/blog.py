import uuid
from contextlib import contextmanager
from selenium.webdriver.ie.webdriver import WebDriver
from playwright.sync_api import Page

from b_logger.entities.steps import StepStatus, Step
from b_logger.entities.exceptions import possible_exceptions
from b_logger.plugin import runtime


class BLogger:

    @staticmethod
    def set_base_url(base_url: str):
        runtime.set_base_url(base_url)

    @staticmethod
    def set_env(env: str):
        runtime.set_env(env)

    @staticmethod
    def set_browser(browser: WebDriver | Page):
        runtime.set_browser(browser)

    @staticmethod
    def param(name, value):
        """
        Add test parameter

        :param name:
        :param value:
        :return:
        """
        runtime.test_report.add_parameter(name, value)

    @staticmethod
    def info(info_str):
        """
        Add any test info

        :param info_str:
        :return:
        """
        runtime.test_report.info = info_str

    @staticmethod
    @contextmanager
    def step(title: str, expected: str = None):
        step_id = uuid.uuid4()

        step = Step(
            id_=step_id,
            title=title
        )

        runtime.start_step(step)

        try:
            yield
            runtime.handle_step_result(step)

        except possible_exceptions as e:
            runtime.handle_step_result(step, e)
            raise e

        finally:
            runtime.finish_step(step)

    @staticmethod
    def print(message, status: StepStatus = StepStatus.NONE):
        mes = Step(title=message, status=status)
        runtime.print_message(mes)

    @staticmethod
    def attach():
        pass
