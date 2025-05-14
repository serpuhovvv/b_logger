import pytest
import yaml
import json
import os
from pathlib import Path
from .utils.paths import pathfinder
from .utils.basedatamodel import BaseDataModel
from .utils.dotdict import DotDict


class LoggerConfig(BaseDataModel):
    project_name: str = None
    env: str = None
    jenkins_build_link = None
    qase: bool = None
    allure: bool = None

    # _instance = None
    #
    # def __new__(cls, path: str = f'{logger_root()}/b_logger.config.yaml'):
    #     if cls._instance is None:
    #         cls._instance = super(LoggerConfig, cls).__new__(cls)
    #         cls._instance._load(path)
    #     return cls._instance

    def __init__(self, path: str = f'{pathfinder.project_root()}/b_logger.config.yaml'):
        conf = self._load(path)

        self.set_project_name(conf.project_name)
        self.set_qase(conf.qase)
        self.set_allure(conf.allure)

    def _load(self, path: str):
        config_path = Path(path)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'Config file not found: {path}')

        with config_path.open('r') as f:
            raw_data = yaml.safe_load(f)
        self._data = DotDict(raw_data)

        return self._data

    def set_project_name(self, project_name: str):
        self.project_name = project_name

    def set_jbl(self, jbl):
        self.jenkins_build_link = jbl

    def set_env(self, env: str):
        self.env = env

    def set_qase(self, qase: bool):
        self.qase = qase

    def set_allure(self, allure: bool):
        self.allure = allure

    def __getattr__(self, item):
        return getattr(self._data, item)

    def __getitem__(self, item):
        return self._data[item]

    # @classmethod
    # def get(cls):
    #     return cls()


logger_config = LoggerConfig()
