from contextlib import ExitStack, contextmanager
from typing import ClassVar

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext, AssetConfig
from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.mocker import Mocker


class RecordOrchestrator:
    _MAPPING: ClassVar = {MockType.HTTP: HTTPMocker}

    @classmethod
    def recorders_from_config(cls, config: AssetConfig) -> list[Mocker]:
        try:
            return [cls._MAPPING[mock_type]() for mock_type in config.mock_types]
        except KeyError as e:
            raise KeyError(f"Unsupported mock types provided {config.mock_types}") from e

    @classmethod
    @contextmanager
    def record(cls, app, config: AssetConfig, action: ActionContext):
        register = MocksRegister()
        with ExitStack() as stack:
            recorders = cls.recorders_from_config(config)
            for r in recorders:
                stack.enter_context(r.record(register, action))
            yield
        register.export_to_vault(app, action, config)
