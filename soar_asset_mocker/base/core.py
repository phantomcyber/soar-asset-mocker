from contextlib import contextmanager

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.mocker.mocker_orchestrator import MockOrchestrator
from soar_asset_mocker.recorder.recorder_orchestrator import RecordOrchestrator


class AssetMocker:
    def __init__(self, types: tuple[MockType, ...] = ()) -> None:
        self._mock_types = set(types)

    def _get_asset_config(self, app):
        config = AssetConfig.from_app(app)
        if self._mock_types:
            config.mock_types = self._mock_types
        return config

    @contextmanager
    def mock_context(self, app, config: AssetConfig, action: ActionContext):
        if not config.is_mocking:
            yield
            return
        app.save_progress(f"[Asset Mocker] {config.description}")
        with MockOrchestrator.mock(config, action):
            yield

    @contextmanager
    def record_context(self, app, config: AssetConfig, action: ActionContext):
        if not config.is_recording:
            yield
            return
        app.save_progress(f"[Asset Mocker] {config.description}")
        with RecordOrchestrator.record(app, config, action):
            yield

    def wrap_core(self, handle):
        def wrapper(app, param):
            config = self._get_asset_config(app)
            action = ActionContext.from_action_run(app, param)
            with self.mock_context(app, config, action):
                with self.record_context(app, config, action):
                    out = handle(app, param)
            if config.active:
                results = app.get_action_results()
                results[-1].update_summary(config.summary)
            return out

        return wrapper

    @classmethod
    def wrap(cls, *mock_types: MockType):
        return cls(mock_types).wrap_core
