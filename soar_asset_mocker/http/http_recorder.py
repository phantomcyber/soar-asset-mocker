from contextlib import contextmanager

from vcr import VCR

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext
from soar_asset_mocker.recorder.recorder import Recorder

from .persisters import RegisterWritePersister


class HTTPRecorder(Recorder):

    def __init__(self):
        super().__init__(MockType.HTTP)

    @contextmanager
    def record(self, register: MocksRegister, action: ActionContext):
        vcr = VCR(record_mode="all")  # Will only record requests
        vcr.persister = RegisterWritePersister(register, action)
        with vcr.use_cassette(self.mock_type.value):
            yield
