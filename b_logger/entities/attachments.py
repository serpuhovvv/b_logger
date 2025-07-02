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
        source: Union[str, Path, bytes, BinaryIO, dict, list, int, float, bool, None] = None,
        name: Optional[str] = None,
        type_: Optional[str] = None,
        _skip_processing: bool = False,
    ):
        self.name = name or f'attachment_{uuid.uuid4()}'
        self.type_ = type_

        if not _skip_processing:
            self._process_attachment(source)

    def _process_attachment(self, source):
        # 1. bytes
        if isinstance(source, bytes):
            self.type_ = 'image/png'
            self.ensure_extension('.png')
            self.__from_bytes(source)

        # 2. JSON supported
        elif isinstance(source, (dict, list, int, float, bool, type(None))):
            self.type_ = 'application/json'
            self.ensure_extension('.json')
            data = json.dumps(source, ensure_ascii=False, indent=2).encode('utf-8')
            self.__from_bytes(data)

        # 3. str
        elif isinstance(source, str):
            if not source.strip():
                print('[BLogger][WARN] Cannot attach empty string')

            path = Path(source)
            if path.exists() and path.is_file():
                self.type_ = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
                self.__from_file(path)
            else:
                try:
                    parsed = json.loads(source)
                    self.type_ = 'application/json'
                    self.ensure_extension('.json')
                    formatted = json.dumps(parsed, ensure_ascii=False, indent=2).encode('utf-8')
                    self.__from_bytes(formatted)
                except json.JSONDecodeError:
                    self.type_ = 'text/plain'
                    self.ensure_extension('.txt')
                    self.__from_bytes(source.encode('utf-8'))

        # 4. Path
        elif isinstance(source, Path):
            if not source.exists() or not source.is_file():
                print(f'[BLogger][WARN] Attachment path is invalid: {source}')
            self.type_ = mimetypes.guess_type(str(source))[0] or 'application/octet-stream'
            self.__from_file(source)

        # 5. File-like (BinaryIO)
        elif hasattr(source, 'read'):
            self.type_ = mimetypes.guess_type(getattr(source, 'name', ''))[0] or 'application/octet-stream'
            self.__from_filelike(source)

        else:
            print(f'[BLogger][WARN] Unsupported attachment source type: {type(source)}')

    def __from_file(self, file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")
        self.ensure_extension(file_path.suffix or '')
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
        path = cls.root / name
        if not path.exists():
            raise FileNotFoundError(f'[BLogger][WARN] Attachment file not found: {path}')
        return cls(path, name=name, type_=type_, _skip_processing=True)

    def ensure_extension(self, ext: str):
        if not self.name.endswith(ext):
            self.name += ext