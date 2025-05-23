import os
import mimetypes
from pathlib import Path
from typing import Union, Optional
from contextlib import contextmanager
from allure_commons.types import AttachmentType

from qase.pytest import qase
import allure

from b_logger.config import b_logger_config
from b_logger.entities.attachments import Attachment


class Integrations:
    qase_enabled: bool = b_logger_config.qase
    allure_enabled: bool = b_logger_config.allure

    @staticmethod
    @contextmanager
    def steps(title, expected):
        if Integrations.qase_enabled and Integrations.allure_enabled:
            with qase.step(title, expected), allure.step(title):
                yield
        elif Integrations.qase_enabled:
            with qase.step(title, expected):
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
    def param(name, value):
        if Integrations.qase_enabled:
            qase.fields((name, value))
        if Integrations.allure_enabled:
            allure.dynamic.parameter(name, value)

    @staticmethod
    def attach(source, attachment: Attachment):
        def _guess_allure_type(filename_or_mime: str) -> AttachmentType:
            mime_type = mimetypes.guess_type(filename_or_mime)[0] \
                if not filename_or_mime.startswith("image/") \
                else filename_or_mime

            return {
                "image/png": AttachmentType.PNG,
                "image/jpeg": AttachmentType.JPG,
                "application/json": AttachmentType.JSON,
                "text/plain": AttachmentType.TEXT,
                "text/html": AttachmentType.HTML,
                "application/xml": AttachmentType.XML,
            }.get(mime_type, AttachmentType.TEXT)

        if Integrations.qase_enabled:
            qase.attach((source, attachment.name, attachment.type_))

        if Integrations.allure_enabled:
            allure_type = _guess_allure_type(attachment.type_)
            allure.attach(source, attachment.name, allure_type)


# def apply_decorators(*decorators):
#     def meta_decorator(func):
#         for decorator in reversed(decorators):
#             func = decorator(func)
#         return func
#     return meta_decorator
