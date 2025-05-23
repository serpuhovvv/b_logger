import pytest
import yaml
import json
import os
from pathlib import Path
from b_logger.utils.paths import pathfinder
from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.dotdict import DotDict


class BLoggerConfig(BaseDataModel):
    project_name: str = None
    env: str = None
    base_url: str = None
    qase: bool = None
    allure: bool = None
    html_settings = None

    def __init__(self, path: str = f'{pathfinder.project_root()}/b_logger.config.yaml'):
        config_data = self._load(path)

        self.set_project_name(config_data.project_name)
        self.set_qase(config_data.qase)
        self.set_allure(config_data.allure)

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

    def set_qase(self, qase: bool):
        self.qase = qase

    def set_allure(self, allure: bool):
        self.allure = allure

    def __getattr__(self, item):
        return getattr(self._data, item)

    def __getitem__(self, item):
        return self._data[item]


b_logger_config = BLoggerConfig()
