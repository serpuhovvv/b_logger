import os
import shutil
from pathlib import Path
from functools import lru_cache, wraps


def clear_directory(directory: str):
    if not os.path.exists(directory):
        return

    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def clear_screenshots():
    clear_directory(f'{screenshots_path()}')
    # for pngfile in os.listdir(f'{screenshots_path()}'):
    #     if pngfile.endswith('.png'):
    #         os.remove(f'{screenshots_path()}/{pngfile}')
    #     else:
    #         pass


def clear_logs():
    clear_directory(f'{logs_path()}')
    # for log in os.listdir(f'{logs_path()}'):
    #     os.remove(f'{logs_path()}/{log}')


def clear_tmp_logs():
    clear_directory(f'{tmp_logs_path()}')
    # for log in os.listdir(f'{tmp_logs_path()}'):
    #     os.remove(f'{tmp_logs_path()}/{log}')


@lru_cache(maxsize=1)
def root_path():
    marker_file = 'conftest.py'
    current_path = Path.cwd()

    while marker_file not in os.listdir(current_path):
        current_path = current_path.parent

    project_root = current_path
    return str(project_root)


@lru_cache(maxsize=5)
def file_path(path):
    marker_file = 'conftest.py'
    current_path = Path.cwd()

    while marker_file not in os.listdir(current_path):
        current_path = current_path.parent

    project_root = current_path
    path_ = project_root / path
    return str(path_)


@lru_cache(maxsize=1)
def b_logger_root():
    return file_path('b_logger')


@lru_cache(maxsize=1)
def logs_path():
    return file_path('logs')


@lru_cache(maxsize=1)
def tmp_logs_path():
    return f'{b_logger_root()}/tmp_logs'


@lru_cache(maxsize=1)
def screenshots_path():
    return file_path('screenshots')
