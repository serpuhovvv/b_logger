import re
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
        content: Union[bytes, Path, BinaryIO, str, dict, list, int, float, bool, None] = None,
        name: Optional[str] = None,
        type_: Optional[str] = None,
        _skip_processing: bool = False,
    ):
        self.name = self._normalize_name(name or f'attachment_{uuid.uuid4()}')
        self.type_ = type_

        if not _skip_processing:
            self._process(content)

    # ---------------------------------------------------------------------
    # MAIN PROCESSOR
    # ---------------------------------------------------------------------
    def _process(self, content):
        if isinstance(content, bytes):
            # Determine by name or default to PNG
            self._detect_type_and_extension(default_ext='.png')
            self._save_from_bytes(content)

        elif isinstance(content, (dict, list, int, float, bool, type(None))):
            # Save JSON
            self._detect_type_and_extension(default_ext='.json')
            data = json.dumps(content, ensure_ascii=False, indent=4).encode('utf-8')
            self._save_from_bytes(data)

        elif isinstance(content, str):
            self._process_str(content)

        elif isinstance(content, Path):
            self._process_path(content)

        elif hasattr(content, 'read'):
            self._process_filelike(content)

        else:
            print(f'[BLogger][WARN] Unsupported attachment content type: {type(content)}')

    # ---------------------------------------------------------------------
    # TYPE & EXT DETECTION
    # ---------------------------------------------------------------------
    def _detect_type_and_extension(self, default_ext: str = '.png'):
        """Try to detect MIME type and ensure proper extension."""
        ext = Path(self.name).suffix.lower()
        if not ext:
            ext = default_ext
            self.name += ext

        self.type_ = self.type_ or mimetypes.types_map.get(ext, 'application/octet-stream')

    # ---------------------------------------------------------------------
    # CONTENT HANDLERS
    # ---------------------------------------------------------------------
    def _process_str(self, content: str):
        if not content.strip():
            print('[BLogger][WARN] Cannot attach empty string')
            return

        # Try JSON first
        try:
            parsed = json.loads(content)
            self._detect_type_and_extension(default_ext='.json')
            formatted = json.dumps(parsed, ensure_ascii=False, indent=4).encode('utf-8')
            self._save_from_bytes(formatted)
        except json.JSONDecodeError:
            # Plain text
            self._detect_type_and_extension(default_ext='.txt')
            self._save_from_bytes(content.encode('utf-8'))

    def _process_path(self, path: Path):
        if not path.exists() or not path.is_file():
            print(f'[BLogger][WARN] Attachment path is invalid: {path}')
            return

        ext = path.suffix or '.bin'
        self.type_ = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        self._ensure_extension(ext)
        self._save_from_file(path)

    def _process_filelike(self, file_obj: BinaryIO):
        """Handles file-like objects."""
        guessed_ext = Path(getattr(file_obj, 'name', '')).suffix or '.bin'
        self.type_ = mimetypes.guess_type(getattr(file_obj, 'name', ''))[0] or 'application/octet-stream'
        self._ensure_extension(guessed_ext)
        data = file_obj.read()
        if isinstance(data, str):
            data = data.encode('utf-8')
        self._save_from_bytes(data)

    # ---------------------------------------------------------------------
    # SAVE METHODS
    # ---------------------------------------------------------------------
    def _save_from_file(self, file_path: Path):
        dest = self.root / self.name
        # dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(file_path, dest)

    def _save_from_bytes(self, data: bytes):
        dest = self.root / self.name
        # dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as f:
            f.write(data)

    # ---------------------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------------------
    def _ensure_extension(self, ext: str):
        ext = ext.lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        if not self.name.lower().endswith(ext):
            base = Path(self.name).stem
            self.name = f"{base}{ext}"

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Cleans up invalid filename characters and ensures uniqueness."""
        clean_name = re.sub(r'[^A-Za-z0-9._-]', '_', name).strip('_')
        existing = set(os.listdir(attachments_path()))
        base = Path(clean_name).stem
        ext = Path(clean_name).suffix
        index = 0
        candidate = clean_name
        while candidate in existing:
            index += 1
            candidate = f'{base}_{index}{ext}'
        return candidate

    # ---------------------------------------------------------------------
    # SERIALIZATION
    # ---------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        name = data.get("name")
        type_ = data.get("type_")
        if not name:
            raise ValueError("Missing 'name' field in attachment dictionary")

        path = cls.root / name
        if not path.exists():
            raise FileNotFoundError(f'[BLogger][WARN] Attachment file not found: {path}')
        return cls(path, name=name, type_=type_,  _skip_processing=True)

    def to_dict(self) -> dict:
        return {"name": self.name, "type_": self.type_}

    def __repr__(self):
        return f"<Attachment name={self.name!r}, type={self.type_!r}>"

# class Attachment(BaseDataModel):
#     root = Path(attachments_path())
#
#     def __init__(
#         self,
#         content: Union[bytes, Path, BinaryIO, str, dict, list, int, float, bool, None] = None,
#         name: Optional[str] = None,
#         type_: Optional[str] = None,
#         _skip_processing: bool = False,
#     ):
#         self.name = name if name else f'attachment_{uuid.uuid4()}'
#         self.type_ = type_
#
#         if not _skip_processing:
#             self._process_attachment(content)
#
#     def _process_attachment(self, content):
#         # 1. bytes
#         if isinstance(content, bytes):
#             self.type_ = mimetypes.types_map.get('.png', 'image/png')
#             self.ensure_extension('.png')
#             self.__from_bytes(content)
#
#         # 2. JSON-serializable (dict, list, int, float, bool, None)
#         elif isinstance(content, (dict, list, int, float, bool, type(None))):
#             self.type_ = mimetypes.types_map.get('.json', 'application/json')
#             self.ensure_extension('.json')
#             data = json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
#             self.__from_bytes(data)
#
#         # 3. str
#         elif isinstance(content, str):
#             if not content.strip():
#                 raise ValueError("[BLogger][WARN] Cannot attach empty string")
#
#             try:
#                 parsed = json.loads(content)
#                 self.type_ = mimetypes.types_map.get('.json', 'application/json')
#                 self.ensure_extension('.json')
#                 formatted = json.dumps(parsed, ensure_ascii=False, indent=2).encode('utf-8')
#                 self.__from_bytes(formatted)
#             except json.JSONDecodeError:
#                 self.type_ = mimetypes.types_map.get('.txt', 'text/plain')
#                 self.ensure_extension('.txt')
#                 self.__from_bytes(content.encode('utf-8'))
#
#         # 4. Path
#         elif isinstance(content, Path):
#             if not content.exists() or not content.is_file():
#                 raise FileNotFoundError(f'[BLogger][WARN] Attachment path is invalid: {content}')
#             self.type_ = mimetypes.guess_type(str(content))[0] or 'application/octet-stream'
#             self.ensure_extension(content.suffix)
#             self.__from_file(content)
#
#         # 5. File-like object
#         elif hasattr(content, 'read'):
#             self.type_ = mimetypes.guess_type(getattr(content, 'name', ''))[0] or 'application/octet-stream'
#             self.ensure_extension(Path(getattr(content, 'name', '')).suffix or '.bin')
#             self.__from_filelike(content)
#
#         else:
#             raise TypeError(f"[BLogger][WARN] Unsupported attachment content type: {type(content)}")
#
#     def __from_file(self, file_path: Path):
#         if not file_path.exists():
#             raise FileNotFoundError(f"Attachment file not found: {file_path}")
#         dest_path = self.root / self.name
#         if not dest_path.exists():
#             shutil.copy2(file_path, dest_path)
#
#     def __from_bytes(self, data: bytes):
#         dest_path = self.root / self.name
#         dest_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(dest_path, 'wb') as f:
#             f.write(data)
#
#     def __from_filelike(self, file_obj: BinaryIO):
#         if isinstance(file_obj, TextIOBase):
#             data = file_obj.read().encode('utf-8')
#         else:
#             data = file_obj.read()
#         self.__from_bytes(data)
#
#     def ensure_extension(self, ext: str):
#         ext = ext.lower()
#         if not ext.startswith('.'):
#             ext = f'.{ext}'
#         current_ext = Path(self.name).suffix.lower()
#         if current_ext != ext:
#             base = Path(self.name).stem
#             self.name = f"{base}{ext}"
#
#     @classmethod
#     def from_dict(cls, data: dict) -> 'Attachment':
#         name = data.get("name")
#         type_ = data.get("type_")
#         if not name:
#             raise ValueError("Missing 'name' field in attachment dictionary")
#         path = cls.root / name
#         if not path.exists():
#             raise FileNotFoundError(f'[BLogger][WARN] Attachment file not found: {path}')
#         return cls(path, name=name, type_=type_, _skip_processing=True)
#
#     def to_dict(self) -> dict:
#         return {
#             "name": self.name,
#             "type_": self.type_,
#         }
#
#     def __repr__(self):
#         return f"<Attachment name={self.name!r}, type={self.type_!r}>"
