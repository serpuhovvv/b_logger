from b_logger.utils.basedatamodel import BaseDataModel
from qase.pytest import qase


class Attachment(BaseDataModel):
    def __init__(self):
        self.name = None
        self.path = None
        qase.attach()