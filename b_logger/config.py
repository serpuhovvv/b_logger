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
    links = None

    def __init__(self, path: str = f'{pathfinder.project_root()}/blog.config.yaml'):
        config_data = self._load(path)

        self.set_project_name(config_data.project_name)
        self.set_qase(config_data.integrations.qase or False)
        self.set_allure(config_data.integrations.allure or False)
        self.set_links(config_data.links or None)

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

    def set_qase(self, qase: bool):
        self.qase = qase

    def set_allure(self, allure: bool):
        self.allure = allure

    # def set_links(self, links):
    #     # for link in links:
    #     self.links = links

    def __getattr__(self, item):
        return getattr(self._data, item)

    def __getitem__(self, item):
        return self._data[item]


blog_config = BLoggerConfig()
