from abc import ABC
from contextlib import contextmanager
from typing import Any

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext


class Mocker(ABC):

    def __init__(self, mock_type: MockType):
        self.mock_type = mock_type
        self.record_buffer: dict[Any, Any] = {}

    @contextmanager
    def mock(self, register: MocksRegister, action: ActionContext):
        raise NotImplementedError
