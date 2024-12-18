from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker import MockType
from soar_asset_mocker.base.exceptions import VaultExportError
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import soar_libs


def test_register_add_entries(mock_register, action_context):
    mock_type = MockType.HTTP

    mock_register.append_mock_recordings([1, 2, 3], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][action_context.params_key] == [
        1,
        2,
        3,
    ]
    mock_register.append_mock_recordings([4, 5, 6], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][action_context.params_key] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_register_get_entries(mock_register, action_context):
    mock_type = MockType.HTTP
    assert mock_register.get_mock_recordings(mock_type, action_context) == []
    mock_register.append_mock_recordings([1, 2, 3], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][action_context.params_key] == [
        1,
        2,
        3,
    ]
    assert mock_register.get_mock_recordings(mock_type, action_context) == [
        1,
        2,
        3,
    ]


def test_export_to_file(mock_register):
    mock_register.export_to_file()
    register_from_file = MocksRegister.from_file(mock_register.export_to_file())
    assert register_from_file == mock_register


def test_export_to_vault(asset_config, action_context, mock_register):
    soar_libs.Vault.create_attachment = MagicMock(return_value={"hash": "123", "succeeded": True})
    soar_libs.phantom.APP_SUCCESS = True
    soar_libs.phantom.APP_JSON_HASH = "hash"
    app = MagicMock()
    app.save_artifact = MagicMock(return_value=[1, 2, 3])
    mock_type = MockType.HTTP

    mock_register.get_filename = MagicMock(return_value="filename")
    mock_register.append_mock_recordings([1, 2, 3], mock_type, action_context)
    mock_register.export_to_vault(app, action_context, asset_config)

    app.save_artifact.assert_called_once_with(
        {
            "name": (
                f"Asset Mock: {asset_config.app_name}\n"
                f"App Run Id:{action_context.app_run_id}\n"
                f"Asset:{action_context.asset_id}\n"
                f"Container:{asset_config.container_id}\n"
                f"Pb Run:{action_context.playbook_run_id}"
            ),
            "container_id": "1",
            "cef": {
                "vaultId": "123",
                "fileHash": "123",
                "file_hash": "123",
                "fileName": "filename",
            },
            "run_automation": False,
            "source_data_identifier": None,
        }
    )


def test_export_to_vault_fails(asset_config, action_context, mock_register):
    soar_libs.Vault.create_attachment = MagicMock(return_value={"hash": "123", "succeeded": False})
    app = MagicMock()
    app.save_artifact = MagicMock(return_value=[1, 2, 3])

    pytest.raises(
        VaultExportError,
        lambda: mock_register.export_to_vault(app, action_context, asset_config),
    )


def test_serialize_register():
    content = {
        MockType.HTTP: {"actions": {"action_id_1": {"param_1": [{"name": "john", "password": BytesIO(bytes(123))}]}}}
    }

    reg = MocksRegister.from_dict(content.copy())
    binary = reg.export_to_file()
    assert reg == MocksRegister.from_file(binary)


def test_redact_register():
    content = {MockType.HTTP: {"actions": {"action_id_1": {"param_1": [{"password": "123"}]}}}}

    reg1 = MocksRegister.from_dict(content.copy())

    content[MockType.HTTP]["actions"]["action_id_1"]["param_1"][0]["password"] = "redacted"

    reg2 = MocksRegister.from_dict(content.copy())

    reg1.redact()
    assert reg1 == reg2


@patch("time.strftime", MagicMock(return_value="0"))
def test_filename(asset_config, action_context):
    assert (
        MocksRegister().get_filename(action_context, asset_config, ".msgpack")
        == "mock_app_asset_asset_1_action_container_1_run_pb_run_id_0.msgpack"
    )
