from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker import MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import soar_libs


def test_register_add_entries(mock_register, action_context, asset_config):
    mock_type = MockType.HTTP

    mock_register.append_mock_recordings([1, 2, 3], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][
        action_context.params_key
    ] == [
        1,
        2,
        3,
    ]
    mock_register.append_mock_recordings([4, 5, 6], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][
        action_context.params_key
    ] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_register_get_entries(mock_register, action_context, asset_config):
    mock_type = MockType.HTTP
    assert mock_register.get_mock_recordings(mock_type, action_context) == []
    mock_register.append_mock_recordings([1, 2, 3], mock_type, action_context)
    assert mock_register.register[mock_type].actions[action_context.id][
        action_context.params_key
    ] == [
        1,
        2,
        3,
    ]
    assert mock_register.get_mock_recordings(mock_type, action_context) == [
        1,
        2,
        3,
    ]


def test_export_to_file(mock_register, tmp_path):
    mock_register.export_to_file()
    nreg = MocksRegister.from_file(mock_register.export_to_file())
    assert nreg == mock_register


def test_export_to_vault(asset_config, action_context, mock_register):
    soar_libs.Vault.create_attachment = MagicMock(
        return_value={"hash": "123", "succeeded": True}
    )
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
            "name": f"Asset Mock - {asset_config.app_name} | {action_context.id}\nAsset:{action_context.asset_id} Container:{asset_config.container_id}\nRun:{action_context.app_run_id}",
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
    soar_libs.Vault.create_attachment = MagicMock(
        return_value={"hash": "123", "succeeded": False}
    )
    app = MagicMock()
    app.save_artifact = MagicMock(return_value=[1, 2, 3])

    pytest.raises(
        Exception,
        lambda: mock_register.export_to_vault(
            app, action_context, asset_config
        ),
    )


def test_redact_register():
    content = {
        MockType.HTTP: {
            "actions": {"action_id_1": {"param_1": [{"password": "123"}]}}
        }
    }

    reg1 = MocksRegister.from_dict(content.copy())

    content[MockType.HTTP]["actions"]["action_id_1"]["param_1"][0][
        "password"
    ] = "redacted"

    reg2 = MocksRegister.from_dict(content.copy())

    reg1.redact()
    assert reg1 == reg2


@patch("time.strftime", MagicMock(return_value="0"))
def test_filename(asset_config, action_context):
    assert (
        MocksRegister().get_filename(action_context, asset_config, ".msgpack")
        == "asset-mock-app_asset_asset_1_action_id_container_1_run_run_1_0.msgpack"
    )
