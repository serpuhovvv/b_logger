# def decor1(func):
#     def wrapper(*args, **kwargs):
#         print("Вызван decor1")
#         return func(*args, **kwargs)
#     return wrapper
#
#
# def decor2(func):
#     def wrapper(*args, **kwargs):
#         print("Вызван decor2")
#         return func(*args, **kwargs)
#     return wrapper
#
#
# def apply_decorators(*decorators):
#     def meta_decorator(func):
#         for decorator in reversed(decorators):  # Применяем в порядке вызова
#             func = decorator(func)
#         return func
#     return meta_decorator
#
#
# @apply_decorators(decor1, decor2)
# def my_function():
#     print("Оригинальная функция")
#
# my_function()

# @contextmanager
# def log_context(name):
#     print(f"Начало {name}")
#     yield
#     print(f"Конец {name}")
#
# def context_decorator(context_manager):
#     def wrapper(func):
#         @wraps(func)
#         def wrapped(*args, **kwargs):
#             with context_manager(func.__name__):
#                 return func(*args, **kwargs)
#         return wrapped
#     return wrapper
#
# @context_decorator(log_context)
# def my_function():
#     print("Выполнение функции")
#
# my_function()

# class log_context(ContextDecorator):
#     def __init__(self, name):
#         self.name = name
#
#     def __enter__(self):
#         print(f"Начало {self.name}")
#         return self
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         print(f"Конец {self.name}")
#
# @log_context("my_function")
# def my_function():
#     print("Выполнение функции")
#
# my_function()
#
#
# import functools
# from contextlib import ContextDecorator as PyContextDecorator
# from contextlib import _GeneratorContextManager as GeneratorContextManager
#
#
# class ContextManager(GeneratorContextManager, PyContextDecorator):
#     """Pass in a generator to the initializer and the resultant object
#     is both a decorator closure and context manager
#     """
#
#     def __init__(self, func, args=(), kwargs=None):
#         if kwargs is None:
#             kwargs = {}
#
#         super().__init__(func, args, kwargs)
#
#
# def contextdecorator(func):
#     """Similar to contextlib.contextmanager except the decorated generator
#     can be used as a decorator with optional arguments.
#     """
#
#     @functools.wraps(func)
#     def helper(*args, **kwargs):
#         is_decorating = len(args) == 1 and callable(args[0])
#
#         if is_decorating:
#             new_func = args[0]
#
#             @functools.wraps(new_func)
#             def new_helper(*args, **kwargs):
#                 instance = ContextManager(func)
#                 return instance(new_func)(*args, **kwargs)
#
#             return new_helper
#         return ContextManager(func, args, kwargs)
#
#     return helper

# import functools
# from contextlib import ContextDecorator, contextmanager
# from typing import Callable, Generator, Optional, Any
#
# class UniversalContext(ContextDecorator):
#     """Объединяет контекстный менеджер и декоратор"""
#
#     def __init__(self, func: Callable[..., Generator], *args: Any, **kwargs: Any):
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#
#     def __enter__(self):
#         """Вход в контекст"""
#         self.gen = self.func(*self.args, **self.kwargs)  # Создаем генератор
#         return next(self.gen)  # Переход к yield
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         """Выход из контекста"""
#         try:
#             next(self.gen)  # Продолжаем выполнение после yield
#         except StopIteration:
#             pass  # Ожидаемое завершение
#
# def contextdecorator(func: Callable[..., Generator]) -> Callable[..., Any]:
#     """Декоратор, который превращает функцию в универсальный контекст"""
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         # Проверяем, вызывается ли декоратор как `@contextdecorator` или `@contextdecorator()`
#         if len(args) == 1 and callable(args[0]):
#             return UniversalContext(func)(args[0])  # Без параметров: оборачиваем функцию
#         return UniversalContext(func, *args, **kwargs)  # С параметрами: создаем экземпляр
#
#     return wrapper