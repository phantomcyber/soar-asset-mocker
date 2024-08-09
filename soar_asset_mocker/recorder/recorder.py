from abc import ABC
from contextlib import contextmanager

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext


class Recorder(ABC):

    def __init__(self, mock_type: MockType):
        self.mock_type = mock_type

    @contextmanager
    def record(self, register: MocksRegister, action: ActionContext):
        raise NotImplementedError
