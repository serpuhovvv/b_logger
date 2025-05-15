import sys
import os
import shutil
from pathlib import Path
from functools import lru_cache, wraps
from typing import Optional, Union, Any, Set


class PathResolver:
    """
    Утилита для определения корня проекта, корня библиотеки и поиска файлов/директорий.

    Usage:
        resolver = PathResolver()
        project_root = resolver.project_root()
        library_root = resolver.library_root()
        path = resolver.find('settings.py', from_root='project')
    """

    def __init__(
            self,
            project_markers: Set[str] = None,
            library_markers: Set[str] = None,
    ):
        # Маркеры, определяющие корень проекта
        self.project_markers = project_markers or {'b_logger.config.yaml', 'requirements.txt', 'conftest.py'}
        # Маркеры, определяющие корень библиотеки
        self.library_markers = library_markers or {'b_logger'}

    @staticmethod
    def _get_possible_roots(cur_file_dir: str) -> Set[str]:
        """Возвращает возможные корни, исходя из текущего пути и sys.path"""
        possible_roots = set()
        cur_file_components = os.path.normpath(cur_file_dir).split(os.sep)

        for path in sys.path:
            possible_root_dir = True
            for cur_file_comp, comp in zip(cur_file_components, os.path.normpath(path).split(os.sep)):
                if cur_file_comp != comp:
                    possible_root_dir = False
            if possible_root_dir:
                possible_roots.add(path)

        return possible_roots

    @lru_cache(maxsize=1)
    def project_root(self) -> Path:
        """
        Найти корень проекта:
        - Сначала ищет вверх от текущей директории (как при запуске из терминала)
        - Потом по sys.path
        """
        current = Path.cwd().resolve()

        # Проверка вверх по директориям
        for parent in [current, *current.parents]:
            if any((parent / marker).exists() for marker in self.project_markers):
                return parent

        # Если не нашли — проверяем sys.path
        for path in sys.path:
            p = Path(path).resolve()
            if any((p / marker).exists() for marker in self.project_markers):
                return p

        raise RuntimeError(f"Не удалось найти корень проекта. Искомые маркеры: {self.project_markers}")

    @lru_cache(maxsize=1)
    def library_root(self) -> Path:
        """
        Найти корень библиотеки, основываясь на расположении этого модуля.
        """
        path = Path(__file__).resolve()
        possible_roots = self._get_possible_roots(str(path))

        for root in possible_roots:
            if any((Path(root) / marker).exists() for marker in self.library_markers):
                return Path(root)

        raise RuntimeError(f"Не удалось найти корень библиотеки. Искомые маркеры: {self.library_markers}")

    def find(
            self,
            name: str,
            from_root: str = 'project',
            include_dirs: bool = True,
            exclude_dirs: tuple[str, ...] = ('.git', '.venv', '__pycache__'),
    ) -> Union[str, Path]:
        """
        Найти файл или директорию по точному имени от указанного корня, исключая служебные папки.
        """
        if from_root == 'project':
            root_path = self.project_root()
        elif from_root == 'library':
            root_path = self.library_root()
        else:
            raise ValueError("from_root must be 'project' or 'library'")

        for p in root_path.rglob("*"):
            # Пропуск директорий, которые находятся в исключённых путях
            if any(ex in p.parts for ex in exclude_dirs):
                continue
            if p.name == name and ((include_dirs and p.is_dir()) or (not include_dirs and p.is_file())):
                return p

        return str(root_path / name)


pathfinder = PathResolver()


def clear_directory(directory: str):
    dir_path = Path(directory)
    if not dir_path.exists():
        return

    for entry in dir_path.iterdir():
        if entry.is_file() or entry.is_symlink():
            entry.unlink()
        elif entry.is_dir():
            clear_directory(str(entry))


def clear_attachments():
    clear_directory(f'{attachments_path()}')


def clear_logs():
    clear_directory(f'{b_logs_path()}')


def clear_tmp_logs():
    clear_directory(f'{b_logs_tmp_path()}')


@lru_cache(maxsize=1)
def b_logs_path():
    return pathfinder.find('b_logs')


@lru_cache(maxsize=1)
def attachments_path():
    return pathfinder.find('b_logs/attachments')


@lru_cache(maxsize=1)
def b_logs_tmp_path():
    return pathfinder.find('b_logs_tmp')


@lru_cache(maxsize=1)
def screenshots_path():
    return pathfinder.find('b_logs/attachments/screenshots')


@lru_cache(maxsize=1)
def b_logs_tmp_reports_path():
    return pathfinder.find('b_logs_tmp/reports')


@lru_cache(maxsize=1)
def b_logs_tmp_steps_path():
    return pathfinder.find('b_logs_tmp/steps')


@lru_cache(maxsize=1)
def b_logs_tmp_preconditions_path():
    return pathfinder.find('b_logs_tmp/preconditions')
