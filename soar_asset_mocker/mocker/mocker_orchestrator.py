from contextlib import ExitStack, contextmanager

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext, AssetConfig
from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.mocker import Mocker


class MockOrchestrator:
    _MAPPING = {MockType.HTTP: HTTPMocker}

    @classmethod
    def mockers_from_config(cls, config: AssetConfig) -> list[Mocker]:
        try:
            return [cls._MAPPING[mock_type]() for mock_type in config.mock_types]
        except KeyError:
            raise KeyError(f"Unsupported mock types provided {config.mock_types}")

    @classmethod
    @contextmanager
    def mock(cls, config: AssetConfig, action: ActionContext):
        register = MocksRegister.from_file(config.mock_file)
        with ExitStack() as stack:
            mockers = cls.mockers_from_config(config)
            for m in mockers:
                stack.enter_context(m.mock(register, action))
            yield
