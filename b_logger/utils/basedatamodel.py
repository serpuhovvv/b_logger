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
        """Кастомный сериализатор для различных типов."""
        if isinstance(obj, BaseDataModel):
            return obj.to_dict()
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, (UUID, datetime, timedelta, Path)):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, defaultdict):
            return dict(obj)
        elif isinstance(obj, dict):
            return {k: BaseDataModel.custom_serializer(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [BaseDataModel.custom_serializer(v) for v in obj]
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
        """Преобразует объект в словарь."""
        def convert(value: Any):
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, (UUID, datetime, timedelta, Path)):
                return str(value)
            if isinstance(value, defaultdict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, list):
                return [convert(v) for v in value]
            if isinstance(value, set):
                return list(value)
            # if value is None or len(value) == 0:
            #     return None
            return value

        return {k: convert(v) for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict):
        """Создание объекта из словаря."""
        obj = cls()

        if isinstance(data, list):
            return data

        for key, value in data.items():
            if hasattr(obj, key):
                # field_value = getattr(obj, key)

                # if (isinstance(field_value, datetime) and isinstance(value, str)
                #         or (value is not None and ':' in value and '-' in value)):
                #     value = datetime.fromisoformat(value)
                # elif isinstance(field_value, UUID) and isinstance(value, str):
                #     value = UUID(value)
                # elif isinstance(field_value, timedelta) and isinstance(value, str):
                #     value = timedelta(seconds=float(value))
                # elif isinstance(field_value, Enum) and isinstance(value, str):
                #     try:
                #         value = field_value.__class__[value]
                #     except KeyError:
                #         pass

                setattr(obj, key, value)
            else:
                obj.__dict__[key] = value
        return obj

    @classmethod
    def from_json(cls, filepath: str):
        """Создание объекта из JSON-файла."""
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)

    # def restore_from_json(self, path: str):
    #     """Восстановить данные из JSON-файла и установить их в атрибуты класса."""
    #     restored_data = self.from_json(path)
    #
    #     # Автоматически устанавливаем данные из восстановленного объекта
    #     for key, value in restored_data.__dict__.items():
    #         if hasattr(self, key):
    #             setattr(self, key, value)
    #         else:
    #             print(f"Warning: {key} не найден в классе {self.__class__.__name__}")
    #
    #     return self

# class BaseDataModel:
#     # Переопределяем __str__, чтобы возвращать строковое представление объекта в формате JSON
#     def __str__(self) -> str:
#         return json.dumps(self,
#                           default=self.custom_serializer,
#                           indent=4,
#                           sort_keys=False
#                           )
#
#     # Custom func to serialize obj
#     @staticmethod
#     def custom_serializer(obj):
#         if isinstance(obj, BaseDataModel):
#             return obj.to_dict()
#         elif isinstance(obj, Enum):
#             return obj.value
#         elif isinstance(obj, (UUID, datetime, timedelta, Path)):
#             return str(obj)
#         elif isinstance(obj, set):
#             return list(obj)
#         elif isinstance(obj, defaultdict):
#             return dict(obj)
#         elif isinstance(obj, dict):
#             return {k: BaseDataModel.custom_serializer(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [BaseDataModel.custom_serializer(v) for v in obj]
#         elif hasattr(obj, '__dict__'):
#             return vars(obj)
#         return str(obj)
#
#     # Method to turn obj to dict
#     def to_dict(self):
#         def convert(value):
#             if isinstance(value, Enum):
#                 return value.name
#             if isinstance(value, (UUID, datetime)):
#                 return str(value)
#             if isinstance(value, defaultdict):
#                 return {k: convert(v) for k, v in value.items()}
#             if isinstance(value, dict):
#                 return {k: convert(v) for k, v in value.items()}
#             if isinstance(value, list):
#                 return [convert(v) for v in value]
#             return value
#
#         return {k: convert(v) for k, v in self.__dict__.items()}
#
#     # Method to serialize obj to json
#     def to_json(self):
#         return json.dumps(self, default=self.custom_serializer, indent=4, sort_keys=False)
#
#     # Method to write obj to json file
#     def to_json_file(self, path):
#         full_path = f'{path}.json'
#         with open(full_path, "w") as file:
#             json.dump(self, file, default=self.custom_serializer, indent=4, sort_keys=False)
#
#     @classmethod
#     def from_dict(cls, data: dict):
#         obj = cls()
#         for key, value in data.items():
#             if hasattr(obj, key):
#                 setattr(obj, key, value)
#             else:
#                 obj.__dict__[key] = value
#         return obj
#
#     # Метод для загрузки объекта из JSON-файла
#     @classmethod
#     def from_json(cls, filepath: str):
#         with open(filepath, "r", encoding="utf-8") as file:
#             data = json.load(file)
#         return cls.from_dict(data)
