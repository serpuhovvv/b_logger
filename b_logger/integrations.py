import json
import mimetypes
import os
from contextlib import contextmanager, ExitStack
from abc import ABC, abstractmethod
from pathlib import Path
from pprint import pformat

from b_logger.config import blog_config
from b_logger.utils.json_handler import process_json


class IntegrationBase(ABC):
    @abstractmethod
    def is_enabled(self) -> bool: ...

    @abstractmethod
    @contextmanager
    def step(self, title, expected=None): ...

    @abstractmethod
    def description(self, text): ...

    @abstractmethod
    def info(self, name, value): ...

    @abstractmethod
    def link(self, url, name): ...

    @abstractmethod
    def attach(self, content, name, type_=None): ...


class AllureAdapter(IntegrationBase):
    def __init__(self):
        try:
            import allure
            from allure_commons.types import AttachmentType
            self._allure = allure
            self._AttachmentType = AttachmentType
        except ImportError:
            self._allure = None

    def is_enabled(self):
        return bool(blog_config.allure) and self._allure is not None

    @contextmanager
    def step(self, title, expected=None):
        if self._allure:
            with self._allure.step(title):
                yield
        else:
            yield

    def description(self, text):
        if self._allure:
            self._allure.dynamic.description(text)

    def info(self, name, value):
        if self._allure:
            try:
                self._allure.attach(process_json(value), name, self._AttachmentType.TEXT)
            except:
                pass

    def link(self, url, name):
        if self._allure:
            self._allure.dynamic.link(url, name=name)

    def attach(self, content, name, type_=None):
        if self._allure:
            try:
                if isinstance(content, (str, Path)) and os.path.exists(str(content)):
                    file_path = Path(content)
                    name = name or file_path.name
                    mime_type = mimetypes.guess_type(file_path)[0]

                    mime_map = {
                        "image/png": self._AttachmentType.PNG,
                        "image/jpeg": self._AttachmentType.JPG,
                        "application/json": self._AttachmentType.JSON,
                        "text/plain": self._AttachmentType.TEXT,
                        "text/html": self._AttachmentType.HTML,
                        "application/xml": self._AttachmentType.XML,
                    }

                    attach_type = mime_map.get(mime_type, self._AttachmentType.TEXT)
                    try:
                        self._allure.attach.file(str(file_path), name, attachment_type=attach_type)
                    except Exception as e:
                        print(f'[AllureAdapter][WARN] Failed to attach file {file_path}: {e}')
                    return

                if isinstance(content, (dict, list)):
                    content = process_json(content)
                    type_ = "application/json"

                if isinstance(content, (int, float, bool)):
                    content = str(content)
                    type_ = "text/plain"

                if isinstance(content, bytes):
                    attach_type = self._AttachmentType.TEXT if not type_ else None
                    self._allure.attach(content, name or "attachment", attach_type)
                    return

                mime_type = (
                    mimetypes.guess_type(type_)[0]
                    if type_ and not type_.startswith("image/")
                    else type_
                )
                mime_map = {
                    "image/png": self._AttachmentType.PNG,
                    "image/jpeg": self._AttachmentType.JPG,
                    "application/json": self._AttachmentType.JSON,
                    "text/plain": self._AttachmentType.TEXT,
                    "text/html": self._AttachmentType.HTML,
                    "application/xml": self._AttachmentType.XML,
                }
                attach_type = mime_map.get(mime_type, self._AttachmentType.TEXT)
                self._allure.attach(str(content), name or "attachment", attach_type)
            except Exception as e:
                print(f'[AllureAdapter][WARN] Failed to attach {name}: {e}')


class QaseAdapter(IntegrationBase):
    def __init__(self):
        try:
            from qase.pytest import qase
            self._qase = qase
        except ImportError:
            self._qase = None

    def is_enabled(self):
        return bool(blog_config.qase) and self._qase is not None

    @contextmanager
    def step(self, title, expected=None):
        if self._qase:
            with self._qase.step(title, expected):
                yield
        else:
            yield

    def description(self, text):
        if self._qase:
            self._qase.description(text)

    def info(self, name, value):
        if self._qase:
            if isinstance(value, (dict, list, tuple, set)):
                content = process_json(value)
                mimetype = 'application/json'
            elif isinstance(value, (str, int, float, bool)):
                content = str(value)
                mimetype = 'text/plain'
            elif isinstance(value, bytes):
                content = value
                mimetype = 'application/octet-stream'
            else:
                content = pformat(value)
                mimetype = 'text/plain'

            try:
                self._qase.attach((content, name, mimetype))
            except:
                pass

    def link(self, url, name):
        if self._qase:
            self._qase.attach((url, 'text/plain', name))

    def attach(self, content, name, type_=None):
        if self._qase:
            try:
                if not type_:
                    if isinstance(content, (dict, list, tuple, set)):
                        content = process_json(content)
                        type_ = 'application/json'
                    elif isinstance(content, (str, int, float, bool)):
                        content = str(content)
                        type_ = 'text/plain'
                    elif isinstance(content, bytes):
                        content = content
                        type_ = 'application/octet-stream'
                    else:
                        content = pformat(content)
                        type_ = 'text/plain'

                self._qase.attach((content, name, type_))
            except Exception as e:
                print(f'[QASEAdapter][WARN] Failed to attach {name}: {e}')


adapters = [QaseAdapter(), AllureAdapter()]


class Integrations:
    @staticmethod
    def enabled():
        return [a for a in adapters if a.is_enabled()]

    @staticmethod
    @contextmanager
    def step(title, expected=None):
        with ExitStack() as stack:
            for adapter in adapters:
                if adapter.is_enabled():
                    stack.enter_context(adapter.step(title, expected))
            yield

    @staticmethod
    def description(text):
        for a in adapters:
            if a.is_enabled():
                a.description(text)

    @staticmethod
    def info(name, value):
        for a in adapters:
            if a.is_enabled():
                a.info(name, value)

    @staticmethod
    def link(url, name):
        for a in adapters:
            if a.is_enabled():
                a.link(url, name)

    @staticmethod
    def attach(content, name, type_):
        for a in adapters:
            if a.is_enabled():
                a.attach(content, name, type_)
