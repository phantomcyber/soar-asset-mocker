import os
from dataclasses import dataclass

from soar_asset_mocker.base.consts import (
    AssetMockerMode,
    AssetMockerScope,
    MockType,
)

from .action_context import ActionContext


@dataclass
class AssetConfig:
    app_name_uid: str
    mode: AssetMockerMode
    mock_file: str
    mock_types: set[MockType]
    container_id: str
    scope: AssetMockerScope

    def description(self, action: ActionContext):
        types_str = ",".join([t.value for t in self.mock_types])
        if self.is_recording(action):
            return f"Recording to container {self.container_id}, used mockers: {types_str}"
        if self.is_mocking(action):
            return f"Mocking, used mockers: {types_str}"

    def summary(self, action: ActionContext):
        return {"Asset Mocker": self.description(action)}

    @property
    def app_name(self):
        return "".join(self.app_name_uid.split("_")[:-1])

    def is_enabled(self, action: ActionContext):
        return (
            self.scope == AssetMockerScope.VPE and action.vpe_test_mode
        ) or (self.scope == AssetMockerScope.ALL)

    def is_mocking(self, action: ActionContext):
        return (
            self.is_enabled(action)
            and self.mode == AssetMockerMode.MOCK
            and self.mock_file
        )

    def is_recording(self, action: ActionContext):
        return self.is_enabled(action) and self.mode == AssetMockerMode.RECORD

    def is_active(self, action: ActionContext):
        return self.is_enabled(action) and (
            self.is_mocking(action) or self.is_recording(action)
        )

    @classmethod
    def _mock_file_from_artifact(cls, app, artifact_id: str): ...

    @classmethod
    def _from_env(cls, app):
        config = app.get_config()
        return cls(
            app_name_uid=config.get("directory"),
            mock_types=set(),
            mock_file=cls._mock_file_from_artifact(
                app, os.getenv("SOAR_AM_ARTIFACT_ID", "")
            ),
            mode=AssetMockerMode(os.getenv("SOAR_AM_MODE", "NONE")),
            scope=AssetMockerScope(os.getenv("SOAR_AM_SCOPE", "VPE")),
            container_id=os.getenv(
                "SOAR_AM_CONTAINER_ID", app.get_container_id()
            ),
        )

    @classmethod
    def _from_app_config(cls, app):
        config = app.get_config()
        if any(
            field not in config
            for field in ["am_mode", "am_file", "am_scope", "am_container_id"]
        ):
            return None
        return cls(
            app_name_uid=config.get("directory"),
            mock_types=set(),
            mock_file=config.get("am_file"),
            mode=AssetMockerMode(config.get("am_mode", "NONE")),
            scope=AssetMockerScope(config.get("am_scope", "VPE")),
            container_id=config.get("am_container_id", app.get_container_id()),
        )

    @classmethod
    def from_app(cls, app):
        config = cls._from_app_config(app)
        if not config:
            config = cls._from_env(app)
        return config
