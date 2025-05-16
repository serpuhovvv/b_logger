from b_logger.config import b_logger_config
from contextlib import contextmanager
from qase.pytest import qase
import allure


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