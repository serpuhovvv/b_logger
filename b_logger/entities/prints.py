import uuid

from b_logger.utils.basedatamodel import BaseDataModel


class Print(BaseDataModel):
    def __init__(self, data):
        self.id = f'print_{uuid.uuid4()}'
        self.title = data
        self.parent_id = None

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id
