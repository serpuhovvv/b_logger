"""
Copyright 2025 Serg Pudikov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from enum import Enum
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from typing import Any


class BaseDataModel:
    indent = 4
    sort_keys = False

    def __str__(self) -> str:
        return self.to_json()

    @staticmethod
    def custom_serializer(obj: Any):
        if isinstance(obj, BaseDataModel):
            return obj.to_dict()
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, (UUID, datetime, timedelta, Path)):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj) if len(obj) != 0 else None
        elif isinstance(obj, defaultdict):
            return dict(obj)
        elif isinstance(obj, dict):
            return {k: BaseDataModel.custom_serializer(v) for k, v in obj.items()} if len(obj) != 0 else None
        elif isinstance(obj, list):
            return [BaseDataModel.custom_serializer(v) for v in obj] if len(obj) != 0 else None
        elif hasattr(obj, '__dict__'):
            return vars(obj)
        return str(obj)

    def to_json(self) -> str:
        return json.dumps(self,
                          default=self.custom_serializer,
                          indent=self.indent,
                          sort_keys=self.sort_keys
                          )

    def to_json_file(self, path: str):
        full_path = f'{path}.json'
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(self,
                      file,
                      default=self.custom_serializer,
                      indent=self.indent,
                      sort_keys=self.sort_keys
                      )

    def to_dict(self) -> dict:
        def convert(value: Any):
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, (UUID, datetime, timedelta, Path)):
                return str(value)
            if isinstance(value, defaultdict):
                return {k: convert(v) for k, v in value.items()} if len(value) != 0 else None
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()} if len(value) != 0 else None
            if isinstance(value, list):
                return [convert(v) for v in value] if len(value) != 0 else None
            if isinstance(value, set):
                return list(value) if len(value) != 0 else None
            return value

        return {k: convert(v) for k, v in self.__dict__.items()}

    @classmethod
    def from_json(cls, filepath: str):
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data, list):
            return data

        obj = cls()

        for key, value in data.items():
            if isinstance(obj, dict):
                obj[key] = value
            elif hasattr(obj, key):
                setattr(obj, key, value)
            else:
                obj.__dict__[key] = value

        return obj
