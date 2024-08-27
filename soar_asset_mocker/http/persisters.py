from vcr.persisters.filesystem import CassetteNotFoundError
from vcr.serialize import deserialize, serialize

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext


class Serializer:
    @staticmethod
    def deserialize(cassette_dict):
        return {"interactions": cassette_dict}

    @staticmethod
    def serialize(cassette_dict):
        return cassette_dict.get("interactions", [])


class RegisterPersister:
    def __init__(self, register: MocksRegister, action: ActionContext) -> None:
        self.action = action
        self.register = register

    def load_cassette(cls, cassette_path, serializer):
        raise CassetteNotFoundError()

    def save_cassette(self, cassette_path, cassette_dict, serializer):
        raise NotImplementedError()


class RegisterWritePersister(RegisterPersister):

    def save_cassette(self, mock_type: str, cassette_dict, serializer):
        self.register.append_mock_recordings(
            serialize(cassette_dict, Serializer),
            MockType(mock_type),
            self.action,
        )


class RegisterReadPersister(RegisterPersister):

    def load_cassette(self, mock_type: str, serializer):
        recordings = self.register.get_mock_recordings(
            MockType(mock_type), self.action
        )
        if len(recordings) == 0:
            raise CassetteNotFoundError
        return deserialize(
            recordings,
            Serializer,
        )
