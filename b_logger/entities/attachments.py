import uuid
import mimetypes
from pathlib import Path

from b_logger.utils.basedatamodel import BaseDataModel
from b_logger.utils.paths import attachments_path


class Attachment(BaseDataModel):
    root = f'{attachments_path()}'

    def __init__(self, path: str, name=None):
        self.name = name or f'attachment_{uuid.uuid4()}'
        self.relpath = path
        self.type = mimetypes.guess_type(path)[0]

    def get_abspath(self):
        return Path(f'{self.root}/{self.relpath}')

    # @staticmethod
    # def get_file_root(path) -> str:
    #     return os.path.basename(path)[0]
