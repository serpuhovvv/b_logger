import allure

from b_logger.config import b_logger_config


class BloggerAllure:
    def __init__(self):
        self.status: bool = b_logger_config.allure

    def allure_step(self):
        if self.status:
            return allure.step
