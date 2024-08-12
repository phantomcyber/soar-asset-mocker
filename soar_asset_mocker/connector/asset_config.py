from dataclasses import dataclass

from soar_asset_mocker.base.consts import AssetMockerMode, MockType


@dataclass
class AssetConfig:
    app_name_uid: str
    mode: AssetMockerMode
    mock_file: str
    mock_types: set[MockType]
    container_id: str

    @property
    def description(self):
        types_str = ",".join([t.value for t in self.mock_types])
        if self.is_recording:
            return f"Recording to container {self.container_id}, used mockers: {types_str}"
        if self.is_mocking:
            return f"Mocking, used mockers: {types_str}"

    @property
    def summary(self):
        return {"Asset Mocker": self.description}

    @property
    def active(self):
        return self.is_mocking or self.is_recording

    @property
    def app_name(self):
        return "".join(self.app_name_uid.split("_")[:-1])

    @property
    def is_mocking(self):
        return self.mode == AssetMockerMode.MOCK and self.mock_file

    @property
    def is_recording(self):
        return self.mode == AssetMockerMode.RECORD

    @classmethod
    def from_app(cls, app):
        config = app.get_config()
        return cls(
            app_name_uid=config.get("directory"),
            mock_types=set(config.get("am_mock_types", [])),
            mode=AssetMockerMode(config.get("am_mode", "NONE")),
            mock_file=config.get("am_file"),
            container_id=config.get("am_container_id", app.get_container_id()),
        )
