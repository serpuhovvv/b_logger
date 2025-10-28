import re
import shutil
import uuid
import mimetypes
import json
from pathlib import Path
from typing import Union, Optional, BinaryIO

from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import attachments_path


class Attachment(BaseDataModel):
    """Handles attachment saving, type detection, naming, and serialization."""

    root = Path(attachments_path())

    def __init__(
        self,
        content: Union[bytes, Path, BinaryIO, str, dict, list, int, float, bool, None] = None,
        name: Optional[str] = None,
        type_: Optional[str] = None,
        _skip_processing: bool = False,
    ):
        self.name = self._sanitize_name(name or f'attachment_{uuid.uuid4()}')
        self.type_ = type_

        if not _skip_processing:
            self._process(content)

    # ---------------------------------------------------------------------
    # MAIN PROCESSOR
    # ---------------------------------------------------------------------
    def _process(self, content):
        if isinstance(content, bytes):
            self._detect_type_and_extension(default_ext='.png')
            self._save_from_bytes(content)

        elif isinstance(content, (dict, list, int, float, bool, type(None))):
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

        try:
            parsed = json.loads(content)
            self._detect_type_and_extension(default_ext='.json')
            formatted = json.dumps(parsed, ensure_ascii=False, indent=4).encode('utf-8')
            self._save_from_bytes(formatted)
        except json.JSONDecodeError:
            self._detect_type_and_extension(default_ext='.txt')
            self._save_from_bytes(content.encode('utf-8'))

    def _process_path(self, path: Path):
        if not path.exists() or not path.is_file():
            print(f'[BLogger][WARN] Attachment path is invalid: {path}')
            return

        ext = path.suffix or '.bin'
        self._ensure_extension(ext)
        self.type_ = self.type_ or mimetypes.guess_type(str(path))[0] or 'application/octet-stream'

        dest = self._unique_path(self.name)
        shutil.copyfile(path, dest)
        self.name = dest.name

    def _process_filelike(self, file_obj: BinaryIO):
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
        dest = self._unique_path(self.name)
        shutil.copy2(file_path, dest)

    def _save_from_bytes(self, data: bytes):
        if isinstance(data, Path):
            print('[BLogger][WARN] Invalid call: _save_from_bytes received a Path object')

        dest = self._unique_path(self.name)
        with open(dest, 'wb') as f:
            f.write(data)

    # ---------------------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------------------
    def _unique_path(self, filename: str) -> Path:
        """Returns a unique path (adds _1, _2, etc. if name already exists)."""
        base = Path(filename).stem
        ext = Path(filename).suffix
        dest = self.root / filename
        index = 1
        while dest.exists():
            dest = self.root / f'{base}_{index}{ext}'
            index += 1
        self.name = dest.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        return dest

    def _ensure_extension(self, ext: str):
        ext = ext.lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        if not self.name.lower().endswith(ext):
            base = Path(self.name).stem
            self.name = f"{base}{ext}"

    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r'[^A-Za-z0-9._-]', '_', name).strip('_')

    # ---------------------------------------------------------------------
    # SERIALIZATION
    # ---------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        name = data.get("name")
        type_ = data.get("type_")
        if not name:
            print(f'[BLogger][WARN] Missing "name" field in attachment dictionary')

        path = cls.root / name
        if not path.exists():
            print(f'[BLogger][WARN] Attachment file not found: {path}')

        return cls(path, name=name, type_=type_, _skip_processing=True)

    def to_dict(self) -> dict:
        return {"name": self.name, "type_": self.type_}

    def __repr__(self):
        return f"<Attachment name={self.name!r}, type={self.type_!r}>"
