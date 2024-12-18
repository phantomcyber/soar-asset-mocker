import time
from dataclasses import asdict, dataclass, field

import msgpack
from dacite import from_dict

from soar_asset_mocker.base.consts import ASSET_MOCKER_VERSION, MockType
from soar_asset_mocker.base.exceptions import VaultExportError
from soar_asset_mocker.base.serializers import decode_unserializable_types, encode_unserializable_types
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.connector.soar_libs import Vault, phantom
from soar_asset_mocker.utils.redactor import redact_nested


@dataclass
class ActionRegister:
    actions: dict[str, dict[str, list]] = field(default_factory=dict)

    def get_recording_register(self, action: ActionContext) -> list:
        register = self.actions.setdefault(action.id, {})
        register.setdefault(action.params_key, [])
        return self.actions[action.id][action.params_key]

    def add_recording(self, recording: list, action: ActionContext) -> None:
        self.get_recording_register(action).extend(recording)

    def redact(self):
        self.actions = redact_nested(self.actions)


@dataclass
class MocksRegister:
    register: dict[str, ActionRegister] = field(
        default_factory=lambda: {mock_type.value: ActionRegister() for mock_type in MockType}
    )

    def get_action_register(self, mock_type: MockType) -> ActionRegister:
        # this can be done with defaultdict, but this state is going to be extracted,
        # so we should be able to represent it with a simple dict
        self.register.setdefault(mock_type.value, ActionRegister())
        return self.register[mock_type.value]

    @classmethod
    def from_dict(cls, d):
        return from_dict(cls, d)

    @classmethod
    def from_file(cls, file: bytes):
        return cls.from_dict(msgpack.unpackb(file, object_hook=decode_unserializable_types))

    def export_to_file(self) -> bytes:
        self.redact()
        return msgpack.packb(
            asdict(self),
            use_bin_type=True,
            default=encode_unserializable_types,
        )

    def get_mock_recordings(self, mock_type: MockType, action: ActionContext) -> list:
        return self.get_action_register(mock_type).get_recording_register(action)

    def append_mock_recordings(self, recording: list, mock_type: MockType, action: ActionContext):
        self.get_action_register(
            mock_type,
        ).add_recording(recording, action)

    @staticmethod
    def get_filename(action: ActionContext, config: AssetConfig, suffix="") -> str:
        return (
            f"mock_{config.app_name}"
            f"_asset_{action.asset_id}_{action.name}"
            f"_container_{config.container_id}"
            f"_run_{action.playbook_run_id}"
            f"_{time.strftime('%Y%m%d-%H%M%S')}{suffix}"
        )

    @staticmethod
    def get_name(action: ActionContext, config: AssetConfig) -> str:
        return (
            f"Asset Mock: {config.app_name}\n"
            f"App Run Id:{action.app_run_id}\n"
            f"Asset:{action.asset_id}\n"
            f"Container:{config.container_id}\n"
            f"Pb Run:{action.playbook_run_id}"
        )

    def redact(self):
        for action_register in self.register.values():
            action_register.redact()

    def export_to_vault(self, app, action: ActionContext, config: AssetConfig):
        name = self.get_name(action, config)
        file_name = self.get_filename(action, config, ".msgpack")
        attach_resp = Vault.create_attachment(
            self.export_to_file(),
            container_id=config.container_id,
            file_name=file_name,
            metadata=self._create_metadata(action, config),
        )
        if attach_resp.get("succeeded"):
            app.save_artifact(self._create_artifact(name, file_name, attach_resp, config.container_id))
        else:
            raise VaultExportError(attach_resp)

    def _create_artifact(self, name, filename, attach_resp, container_id) -> dict:
        return {
            "name": name,
            "container_id": container_id,
            "cef": {
                "vaultId": attach_resp[phantom.APP_JSON_HASH],
                "fileHash": attach_resp[phantom.APP_JSON_HASH],
                "file_hash": attach_resp[phantom.APP_JSON_HASH],
                "fileName": filename,
            },
            "run_automation": False,
            "source_data_identifier": None,
        }

    def _create_metadata(self, action: ActionContext, config: AssetConfig) -> dict:
        return {
            "playbook_run_id": action.playbook_run_id,
            "action_run_id": action.action_run_id,
            "app_run_id": action.app_run_id,
            "container_id": config.container_id,
            "asset_id": action.asset_id,
            "app_name": config.app_name,
            "playbook_name": action.playbook_name,
            "action_name": action.name,
            "asset_mocker_scope": config.scope.value,
            "asset_mocker_version": ASSET_MOCKER_VERSION,
        }
