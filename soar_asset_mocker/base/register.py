import time
from dataclasses import asdict, dataclass, field

import msgpack
from dacite import from_dict

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.connector.soar_libs import Vault, phantom
from soar_asset_mocker.utils.redactor import redact_nested


@dataclass
class ActionRegister:
    actions: dict[str, dict[str, list]] = field(default_factory=lambda: {})

    def get_recording_register(self, action: ActionContext) -> list:
        register = self.actions.setdefault(action.id, {})
        register.setdefault(action.params_key, [])
        return self.actions[action.id][action.params_key]

    def add_recording(self, recording: list, action: ActionContext) -> None:
        self.get_recording_register(action).extend(redact_nested(recording))

    def redact(self):
        self.actions = redact_nested(self.actions)


@dataclass
class MocksRegister:
    register: dict[str, ActionRegister] = field(
        default_factory=lambda: {
            mock_type.value: ActionRegister() for mock_type in MockType
        }
    )

    def get_action_register(self, mock_type: MockType) -> ActionRegister:
        # this can be done with defaultdict, but this state is going to be extracted, so we should be able to represent it with simple dict
        self.register.setdefault(mock_type.value, ActionRegister())
        return self.register[mock_type.value]

    @classmethod
    def from_dict(cls, d):
        return from_dict(cls, d)

    @classmethod
    def from_file(cls, file: str):
        return cls.from_dict(msgpack.unpackb(file))

    def export_to_file(self) -> str:
        self.redact()
        return msgpack.packb(asdict(self), use_bin_type=True)

    def get_mock_recordings(self, mock_type: MockType, action: ActionContext):
        return self.get_action_register(mock_type).get_recording_register(
            action
        )

    def append_mock_recordings(
        self, recording: list, mock_type: MockType, action: ActionContext
    ):
        self.get_action_register(
            mock_type,
        ).add_recording(recording, action)

    @staticmethod
    def get_filename(action: ActionContext, config: AssetConfig, suffix=""):
        print(action, config)
        return f"asset-mock-{config.app_name}_asset_{action.asset_id}_{action.id}_container_{config.container_id}_run_{action.app_run_id}_{time.strftime('%Y%m%d-%H%M%S')}{suffix}"

    @staticmethod
    def get_name(action: ActionContext, config: AssetConfig):
        print(action, config)
        return f"Asset Mock - {config.app_name} | {action.id}\nAsset:{action.asset_id} Container:{config.container_id}\nRun:{action.app_run_id}"

    def redact(self):
        for action_register in self.register.values():
            action_register.redact()

    def export_to_vault(self, app, action: ActionContext, config: AssetConfig):
        attach_resp = None
        name = self.get_name(action, config)
        file_name = self.get_filename(action, config, ".msgpack")
        attach_resp = Vault.create_attachment(
            self.export_to_file(),
            container_id=config.container_id,
            file_name=file_name,
        )
        if attach_resp.get("succeeded"):
            # Create vault artifact
            ret_val, msg, _ = app.save_artifact(
                self._create_artifact(
                    name, file_name, attach_resp, config.container_id
                )
            )
        else:
            raise Exception(attach_resp)

    def _create_artifact(self, name, filename, attach_resp, container_id):
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
