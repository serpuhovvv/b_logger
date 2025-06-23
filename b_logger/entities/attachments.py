import shutil
import uuid
import mimetypes
import json
import os
from pathlib import Path
from typing import Union, Optional, BinaryIO

from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import attachments_path


class Attachment(BaseDataModel):
    root = Path(attachments_path())

    def __init__(
        self,
        source: Union[str, Path, bytes, BinaryIO, dict, list, int, float, None] = None,
        name: Optional[str] = None,
        type_: Optional[str] = None,
        _skip_processing: bool = False,  # внутренний флаг для from_dict
    ):
        self.name = name or f'attachment_{uuid.uuid4()}'
        self.type_ = type_

        if not _skip_processing:
            self._process_attachment(source)

    def _process_attachment(self, source):
        if isinstance(source, bytes):
            self.type_ = 'image/png'
            if not self.name.endswith('.png'):
                self.name += '.png'
            self.__from_bytes(source)

        elif isinstance(source, (dict, list, int, float, bool, type(None))):
            self.type_ = 'application/json'
            if not self.name.endswith('.json'):
                self.name += '.json'
            data = json.dumps(source, ensure_ascii=False, indent=2).encode('utf-8')
            self.__from_bytes(data)

        elif isinstance(source, str):
            path = Path(source)
            if path.exists():
                self.type_ = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
                self.__from_file(path)
            else:
                try:
                    parsed = json.loads(source)
                    self.type_ = 'application/json'
                    if not self.name.endswith('.json'):
                        self.name += '.json'
                    self.__from_bytes(json.dumps(parsed, ensure_ascii=False, indent=2).encode('utf-8'))
                except json.JSONDecodeError:
                    raise ValueError("String source must be a path or valid JSON")

        elif isinstance(source, Path):
            self.type_ = mimetypes.guess_type(str(source))[0] or 'application/octet-stream'
            self.__from_file(source)

        elif hasattr(source, 'read'):
            self.type_ = mimetypes.guess_type(getattr(source, 'name', ''))[0] or 'application/octet-stream'
            self.__from_filelike(source)

        else:
            raise TypeError(f"Unsupported attachment source type: {type(source)}")

    def __from_file(self, file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        ext = file_path.suffix or ''
        if not self.name.endswith(ext):
            self.name += ext

        dest_path = self.root / self.name
        if not dest_path.exists():
            shutil.copy2(file_path, dest_path)

    def __from_bytes(self, data: bytes):
        dest_path = self.root / self.name
        with open(dest_path, 'wb') as f:
            f.write(data)

    def __from_filelike(self, file_obj: BinaryIO):
        data = file_obj.read()
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.__from_bytes(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        name = data.get("name")
        type_ = data.get("type_")

        # Проверка, что файл физически существует
        path = cls.root / name
        if not path.exists():
            raise FileNotFoundError(f"Attachment file not found: {path}")

        # Возвращаем объект без повторной обработки файла
        return cls(path, name=name, type_=type_, _skip_processing=True)