import os
import mimetypes
from pathlib import Path
from typing import Union, Optional

from allure_commons.types import AttachmentType

from b_logger.config import b_logger_config
from contextlib import contextmanager
from qase.pytest import qase
import allure


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
    def attach(object_: Union[str, bytes, Path], name: str, type_: Optional[str] = None):
        def _guess_allure_type(filename_or_mime: str) -> AttachmentType:
            mime_type = mimetypes.guess_type(filename_or_mime)[0] if not filename_or_mime.startswith("image/") else filename_or_mime

            return {
                "image/png": AttachmentType.PNG,
                "image/jpeg": AttachmentType.JPG,
                "application/json": AttachmentType.JSON,
                "text/plain": AttachmentType.TEXT,
                "text/html": AttachmentType.HTML,
                "application/xml": AttachmentType.XML,
            }.get(mime_type, AttachmentType.TEXT)

        if Integrations.qase_enabled:
            qase.attach((object_, name, type_))

        if Integrations.allure_enabled:
            allure_type = _guess_allure_type(type_ or name)

            if isinstance(object_, Path):
                with open(object_, "rb") as f:
                    allure.attach(f.read(), name=name, attachment_type=allure_type)
            elif isinstance(object_, str) and os.path.exists(object_):
                with open(object_, "rb") as f:
                    allure.attach(f.read(), name=name, attachment_type=allure_type)
            else:
                allure.attach(object_, name=name, attachment_type=allure_type)


# def apply_decorators(*decorators):
#     def meta_decorator(func):
#         for decorator in reversed(decorators):
#             func = decorator(func)
#         return func
#     return meta_decorator
