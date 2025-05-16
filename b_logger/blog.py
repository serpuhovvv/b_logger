import uuid
from contextlib import contextmanager

import allure
import pytest
from selenium.webdriver.ie.webdriver import RemoteWebDriver, WebDriver
from playwright.sync_api import Page

from b_logger.entities.steps import StepStatus, Step
from b_logger.entities.exceptions import possible_exceptions
from b_logger.plugin import runtime
from b_logger.config import b_logger_config
from qase.pytest import qase


class Integrations:
    qase_enabled = b_logger_config.qase
    allure_enabled = b_logger_config.allure

    @staticmethod
    @contextmanager
    def steps(title):
        if Integrations.qase_enabled and Integrations.allure_enabled:
            with qase.step(title), allure.step(title):
                yield
        elif Integrations.qase_enabled:
            with qase.step(title):
                yield
        elif Integrations.allure_enabled:
            with allure.step(title):
                yield
        else:
            yield

    @staticmethod
    def description(description):
        if Integrations.qase_enabled:
            qase.description(description)
        if Integrations.allure_enabled:
            allure.dynamic.description(description)

    @staticmethod
    def attach():
        if Integrations.qase_enabled:
            qase.attach()
        if Integrations.allure_enabled:
            allure.attach()


class BLogger:

    @staticmethod
    def set_base_url(base_url: str):
        runtime.set_base_url(base_url)

    @staticmethod
    def set_env(env: str):
        runtime.set_env(env)

    @staticmethod
    def set_browser(browser: RemoteWebDriver | WebDriver | Page):
        runtime.set_browser(browser)

    @staticmethod
    def description(description):
        Integrations.description(description)
        runtime.test_report.description = description

        return pytest.mark.blog_description(description=description)

    @staticmethod
    def param(name, value):
        """
        Add test parameter

        :param name:
        :param value:
        :return:
        """
        runtime.test_report.add_parameter(name, value)

        return pytest.mark.blog_param(name=name, value=value)

    @staticmethod
    def info(info_str):
        """
        Leave any info or note about test run before or during execution

        :param info_str:
        :return:
        """
        runtime.test_report.add_info(info_str)

    @staticmethod
    @contextmanager
    def step(title: str, expected: str = None):
        with Integrations.steps(title):
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

    @staticmethod
    def known_bug(description, url):
        return pytest.mark.blog_known_bug(description=description, url=url)