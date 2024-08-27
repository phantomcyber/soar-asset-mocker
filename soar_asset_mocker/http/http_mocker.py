from contextlib import contextmanager

from vcr import VCR
from vcr.errors import CannotOverwriteExistingCassetteException

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.exceptions import MissingRecordingException
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext
from soar_asset_mocker.mocker.mocker import Mocker

from .persisters import RegisterReadPersister, RegisterWritePersister


class HTTPMocker(Mocker):

    def __init__(self):
        super().__init__(MockType.HTTP)

    @contextmanager
    def mock(self, register: MocksRegister, action: ActionContext):
        # TODO Add recording/mocking modes to Asset Mocker configuration
        vcr = VCR(record_mode="none")  # Will throw error if mock is missing
        vcr.persister = RegisterReadPersister(register, action)
        with vcr.use_cassette(self.mock_type.value):
            try:
                yield
            except CannotOverwriteExistingCassetteException:
                raise MissingRecordingException

    @contextmanager
    def record(self, register: MocksRegister, action: ActionContext):
        vcr = VCR(record_mode="all")  # Will only record requests
        vcr.persister = RegisterWritePersister(register, action)
        with vcr.use_cassette(self.mock_type.value):
            yield
