import shutil
import uuid
import mimetypes
import os
from pathlib import Path
from typing import Union, Optional, BinaryIO

from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import attachments_path


class Attachment(BaseDataModel):
    root = Path(attachments_path())

    def __init__(
        self,
        source: Union[str, Path, bytes, BinaryIO],
        name: Optional[str] = None
    ):
        self.name = name or f'attachment_{uuid.uuid4()}'

        if isinstance(source, bytes):
            self.type = 'image/png'
            if not self.name.endswith('.png'):
                self.name += '.png'
            self._from_bytes(source)

        elif isinstance(source, (str, Path)):
            path = Path(source)
            self.type = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
            self._from_file(path)

        elif hasattr(source, 'read'):  # file-like
            self.type = mimetypes.guess_type(getattr(source, 'name', 'attachment'))[0] or 'application/octet-stream'
            self._from_filelike(source)

        else:
            raise TypeError(f"Unsupported attachment source type: {type(source)}")

    def _from_file(self, file_path: Path):
        if not file_path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        ext = file_path.suffix or ''
        if not self.name.endswith(ext):
            self.name += ext

        dest_path = self.root / self.name

        if not os.path.exists(dest_path):
            shutil.copy2(file_path, dest_path)

    def _from_bytes(self, data: bytes):
        dest_path = self.root / self.name
        with open(dest_path, 'wb') as f:
            f.write(data)

    def _from_filelike(self, file_obj: BinaryIO):
        data = file_obj.read()
        if isinstance(data, str):
            data = data.encode('utf-8')
        self._from_bytes(data)