from dataclasses import dataclass
from typing import Optional

from soar_asset_mocker.base.consts import AssetMockerMode, AssetMockerScope, MockType
from soar_asset_mocker.base.settings import EnvVariables
from soar_asset_mocker.connector.soar_libs import vault_info

from .action_context import ActionContext


@dataclass
class AssetConfig:
    app_name_uid: str
    mode: AssetMockerMode
    mock_file: bytes
    mock_types: set[MockType]
    container_id: str
    scope: AssetMockerScope

    def description(self, action: ActionContext):
        types_str = " ,".join(t.value for t in self.mock_types)
        if self.is_recording(action):
            return f"Recording to container {self.container_id}, used mockers: {types_str}"
        if self.is_mocking(action):
            return f"Mocking, used mockers: {types_str}"
        return "Asset Mocker unused"

    def summary(self, action: ActionContext):
        return {"Asset Mocker": self.description(action)}

    @property
    def app_name(self):
        """
        SOAR APP UID contains uuid and app name, formatted as: {uuid}_{name}
        for ex. splunk_app_395196a3-b4f8-4c3d-982d-864045242adf1
        """
        return "".join(self.app_name_uid.split("_")[:-1])

    def is_enabled(self, action: ActionContext):
        return (self.scope is AssetMockerScope.VPE and action.vpe_test_mode) or (self.scope is AssetMockerScope.ALL)

    def is_mocking(self, action: ActionContext):
        return self.is_enabled(action) and self.mode is AssetMockerMode.MOCK and self.mock_file

    def is_recording(self, action: ActionContext):
        return self.is_enabled(action) and self.mode is AssetMockerMode.RECORD

    def is_active(self, action: ActionContext):
        return self.is_enabled(action) and (self.is_mocking(action) or self.is_recording(action))

    @staticmethod
    def _parse_container_id(app, input_id: str) -> Optional[int]:
        if not input_id:
            return None
        try:
            return int(input_id)
        except ValueError:
            app.save_progress(f"[Asset Mocker] Container ID env is not a proper integer: {input_id}")
            return None

    @classmethod
    def _mock_file_from_artifact(
        cls,
        app,
        vault_id: str = "",
        file_name: str = "",
        container_id: Optional[int] = None,
    ):
        if not (vault_id or file_name or container_id):
            return ""
        success, message, info = vault_info(vault_id=vault_id, container_id=container_id, file_name=file_name)
        if not success:
            app.save_progress(f"[Asset Mocker] Couldn't fetch {vault_id}, reason: {message}")
            return ""
        recording_file = info[0]
        with open(recording_file["path"], "rb") as f:
            content = f.read()
        app.save_progress(f"[Asset Mocker] Loaded recording file: {recording_file['name']}")
        return content

    @classmethod
    def _from_env(cls, app):
        config = app.get_config()
        envs = EnvVariables()
        mode = AssetMockerMode(envs.MODE)
        # Load only for mock mode
        mock_file = (
            cls._mock_file_from_artifact(
                app,
                vault_id=envs.FILE_VAULT_ID,
                container_id=cls._parse_container_id(app, envs.FILE_CONTAINER_ID),
                file_name=envs.FILE_NAME,
            )
            if mode is AssetMockerMode.MOCK
            else ""
        )
        return cls(
            app_name_uid=config.get("directory"),
            mock_types=set(),
            mock_file=mock_file,
            mode=mode,
            scope=AssetMockerScope(envs.SCOPE),
            container_id=envs.CONTAINER_ID or app.get_container_id(),
        )

    @classmethod
    def _from_app_config(cls, app):
        config = app.get_config()
        if any(field not in config for field in ("am_mode", "am_file", "am_scope", "am_container_id")):
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
