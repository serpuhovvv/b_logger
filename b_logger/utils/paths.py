import sys
import os
import shutil
from pathlib import Path
from functools import lru_cache, wraps
from typing import Optional, Union, Any, Set


class PathFinder:
    """
    Utility for defining library and project roots and for file search

    Usage:
        pathfinder = PathResolver()
        project_root = pathfinder.project_root()
        library_root = pathfinder.library_root()
        path = pathfinder.find('settings.py', from_root='project')
    """

    def __init__(
            self,
            project_markers: Set[str] = None,
            library_markers: Set[str] = None,
    ):
        # Маркеры, определяющие корень проекта
        self.project_markers = project_markers or {'blog.config.yaml', 'requirements.txt', 'conftest.py'}
        # Маркеры, определяющие корень библиотеки
        self.library_markers = library_markers or {'plugin.py', 'b_logger'}

    @staticmethod
    def _get_possible_roots(cur_file_dir: str) -> Set[str]:
        """
        Returns possible roots based on current path ans sys.path"""
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
        Find project root
        """
        current = Path.cwd().resolve()

        # Search directory up
        for parent in [current, *current.parents]:
            if any((parent / marker).exists() for marker in self.project_markers):
                return parent

        # Search through sys.path
        for path in sys.path:
            p = Path(path).resolve()
            if any((p / marker).exists() for marker in self.project_markers):
                return p

        raise RuntimeError(f"Unable to find project root. Markers to search through: {self.project_markers}")

    @lru_cache(maxsize=1)
    def library_root(self) -> Path:
        """
        Find library root
        """
        path = Path(__file__).resolve()
        possible_roots = self._get_possible_roots(str(path))

        for root in possible_roots:
            if any((Path(root) / marker).exists() for marker in self.library_markers):
                return Path(root)

        raise RuntimeError(f'Unable to find library root. '
                           f'Probably you forgot to add "blog.config.yaml" to your project')

    def find(
            self,
            name: str,
            from_root: str = 'project',
            include_dirs: bool = True,
            exclude_dirs: tuple[str, ...] = ('.git', '.venv', '__pycache__'),
    ) -> Union[str, Path]:
        """
        Search for file by its name
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


pathfinder = PathFinder()


def init_dirs():
    os.makedirs(f'{b_logs_path()}', exist_ok=True)
    os.makedirs(f'{attachments_path()}', exist_ok=True)
    os.makedirs(f'{static_path()}', exist_ok=True)

    os.makedirs(f'{b_logs_tmp_path()}', exist_ok=True)
    os.makedirs(f'{b_logs_tmp_reports_path()}', exist_ok=True)
    os.makedirs(f'{b_logs_tmp_steps_path()}', exist_ok=True)

    clear_b_logs()
    clear_b_logs_tmp()

    for filename in ("scripts.js", "styles.css"):
        src = Path(pathfinder.library_root()) / f'b_logger/templates/{filename}'
        dst = Path(static_path()) / filename

        if src.exists():
            shutil.copyfile(src, dst)
        else:
            print(f'[BLogger][WARN] static file not found: {src}')


def clear_directory(directory: str, rmdir=False):
    dir_path = Path(directory)
    if not dir_path.exists():
        return

    for entry in dir_path.iterdir():
        if entry.is_file() or entry.is_symlink():
            entry.unlink()
        elif entry.is_dir():
            clear_directory(str(entry))

        if rmdir:
            entry.rmdir()

    if rmdir:
        dir_path.rmdir()


@lru_cache(maxsize=1)
def b_logs_path():
    return pathfinder.find('b_logs')


@lru_cache(maxsize=1)
def attachments_path():
    return pathfinder.find('b_logs/attachments')


@lru_cache(maxsize=1)
def static_path():
    return pathfinder.find('b_logs/static')


@lru_cache(maxsize=1)
def b_logs_tmp_path():
    return pathfinder.find('b_logs_tmp')


@lru_cache(maxsize=1)
def b_logs_tmp_reports_path():
    return pathfinder.find('b_logs_tmp/reports')


@lru_cache(maxsize=1)
def b_logs_tmp_steps_path():
    return pathfinder.find('b_logs_tmp/steps')


def clear_b_logs():
    clear_directory(f'{b_logs_path()}')


def clear_attachments():
    clear_directory(f'{attachments_path()}')


def clear_b_logs_tmp(rmdir=False):
    clear_directory(f'{b_logs_tmp_path()}', rmdir)
