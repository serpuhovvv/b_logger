import json
import mimetypes
from contextlib import contextmanager, ExitStack
from abc import ABC, abstractmethod
from pprint import pformat


from b_logger.config import blog_config
from b_logger.entities.attachments import Attachment


# try:
#     from qase.pytest import qase
# except Exception as e:
#     qase = None
#     blog_config.qase = False
#     print(f'[WARN] Qase import error: {e}')
#
# try:
#     import allure
#     from allure_commons.types import AttachmentType
# except Exception as e:
#     allure = None
#     AttachmentType = None
#     blog_config.allure = False
#     print(f'[WARN] Allure import error: {e}')


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
    def attach(self, content, name, type_): ...


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
        if not self._allure:
            return

        try:
            # self._allure.dynamic.parameter(name, value)
            self._allure.attach(str(value), name, self._AttachmentType.TEXT)
        except Exception:
            try:
                self._allure.dynamic.parameter(name, value)
                # self._allure.attach(str(value), name, self._AttachmentType.TEXT)
            except Exception:
                print(f'{name}: {value}')

    def link(self, url, name):
        if self._allure:
            self._allure.dynamic.link(url, name=name)

    def attach(self, content, name, type_):
        if not self._allure:
            return

        mime_type = mimetypes.guess_type(type_)[0] \
            if not type_.startswith("image/") \
            else type_

        mime_map = {
            "image/png": self._AttachmentType.PNG,
            "image/jpeg": self._AttachmentType.JPG,
            "application/json": self._AttachmentType.JSON,
            "text/plain": self._AttachmentType.TEXT,
            "text/html": self._AttachmentType.HTML,
            "application/xml": self._AttachmentType.XML,
        }

        attach_type = mime_map.get(mime_type, self._AttachmentType.TEXT)
        self._allure.attach(content, name, attach_type)


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
                content = json.dumps(value, indent=2, ensure_ascii=False)
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

            self._qase.attach((content, name, mimetype))

    def link(self, url, name):
        pass

    def attach(self, content, name, type_):
        if self._qase:
            self._qase.attach((content, name, type_))


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

#
# try:
#     from qase.pytest import qase
# except Exception as e:
#     qase = None
#     blog_config.qase = False
#     print(f'[WARN] Qase import error: {e}')
#
# try:
#     import allure
#     from allure_commons.types import AttachmentType
# except Exception as e:
#     allure = None
#     AttachmentType = None
#     blog_config.allure = False
#     print(f'[WARN] Allure import error: {e}')


# class Integrations:
#     qase_enabled: bool = blog_config.qase
#     allure_enabled: bool = blog_config.allure
#
#     @staticmethod
#     @contextmanager
#     def step(title, expected):
#         if Integrations.qase_enabled and Integrations.allure_enabled:
#             with qase.step(title, expected), allure.step(title):
#                 yield
#         elif Integrations.qase_enabled:
#             with qase.step(title, expected):
#                 yield
#         elif Integrations.allure_enabled:
#             with allure.step(title):
#                 yield
#         else:
#             yield
#
#     @staticmethod
#     def description(description):
#         if Integrations.qase_enabled:
#             qase.description(description)
#         if Integrations.allure_enabled:
#             allure.dynamic.description(description)
#
#     @staticmethod
#     def info(name, value):
#         if Integrations.qase_enabled:
#             qase.fields((name, value))
#         if Integrations.allure_enabled:
#             allure.dynamic.parameter(name, value)
#
#     @staticmethod
#     def link(url):
#         if Integrations.qase_enabled:
#             qase.id(url)
#
#         if Integrations.allure_enabled:
#             allure.dynamic.link(url)
#
#
#     @staticmethod
#     def attach(source, attachment: Attachment):
#         def _guess_allure_type(filename_or_mime: str) -> AttachmentType:
#             mime_type = mimetypes.guess_type(filename_or_mime)[0] \
#                 if not filename_or_mime.startswith("image/") \
#                 else filename_or_mime
#
#             return {
#                 "image/png": AttachmentType.PNG,
#                 "image/jpeg": AttachmentType.JPG,
#                 "application/json": AttachmentType.JSON,
#                 "text/plain": AttachmentType.TEXT,
#                 "text/html": AttachmentType.HTML,
#                 "application/xml": AttachmentType.XML,
#             }.get(mime_type, AttachmentType.TEXT)
#
#         if Integrations.qase_enabled:
#             qase.attach((source, attachment.name, attachment.type_))
#
#         if Integrations.allure_enabled:
#             allure_type = _guess_allure_type(attachment.type_)
#             allure.attach(source, attachment.name, allure_type)


# def apply_decorators(*decorators):
#     def meta_decorator(func):
#         for decorator in reversed(decorators):
#             func = decorator(func)
#         return func
#     return meta_decorator
