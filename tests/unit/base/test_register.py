from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker import consts
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector import ActionContext, AssetConfig, soar_libs


def _get_test_register():
    return (
        MocksRegister(),
        consts.MockType.HTTP,
        ActionContext("id", {"param": 1}, "run_1", "action_1", "asset_1"),
    )


def _get_filled_register():
    return MocksRegister.from_dict(
        {
            "register": {
                consts.MockType.HTTP.value: {
                    "actions": {"action_id_1": {"param_1": [1, 2, 3]}}
                }
            }
        }
    )


def test_register_add_entries():
    mocks, mock_type, action = _get_test_register()

    mocks.append_mock_recordings([1, 2, 3], mock_type, action)
    assert mocks.register[mock_type].actions[action.id][action.params_key] == [
        1,
        2,
        3,
    ]
    mocks.append_mock_recordings([4, 5, 6], mock_type, action)
    assert mocks.register[mock_type].actions[action.id][action.params_key] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_register_get_entries():
    mocks, mock_type, action = _get_test_register()
    assert mocks.get_mock_recordings(mock_type, action) == []
    mocks.append_mock_recordings([1, 2, 3], mock_type, action)
    assert mocks.register[mock_type].actions[action.id][action.params_key] == [
        1,
        2,
        3,
    ]
    assert mocks.get_mock_recordings(mock_type, action) == [1, 2, 3]


def test_export_to_file(tmp_path):
    reg = _get_filled_register()
    reg.export_to_file()
    nreg = MocksRegister.from_file(reg.export_to_file())
    assert nreg == reg


def test_export_to_vault():
    soar_libs.Vault.create_attachment = MagicMock(
        return_value={"hash": "123", "succeeded": True}
    )
    soar_libs.phantom.APP_SUCCESS = True
    soar_libs.phantom.APP_JSON_HASH = "hash"
    app = MagicMock()
    app.save_artifact = MagicMock(return_value=[1, 2, 3])

    mocks, mock_type, action = _get_test_register()
    config = AssetConfig(
        "app_uid",
        consts.AssetMockerMode.RECORD,
        "",
        [mock_type],
        "1",
        action,
        "ALL",
    )
    mocks.get_filename = MagicMock(return_value="filename")
    mocks.append_mock_recordings([1, 2, 3], mock_type, action)
    mocks.export_to_vault(app, action, config)

    app.save_artifact.assert_called_once_with(
        {
            "name": f"Asset Mock - {config.app_name} | {action.id}\nAsset:{action.asset_id} Container:{config.container_id}\nRun:{action.app_run_id}",
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


def test_export_to_vault_fails():
    soar_libs.Vault.create_attachment = MagicMock(
        return_value={"hash": "123", "succeeded": False}
    )
    app = MagicMock()
    app.save_artifact = MagicMock(return_value=[1, 2, 3])

    mocks, mock_type, action = _get_test_register()
    config = AssetConfig(
        "app_uid",
        consts.AssetMockerMode.RECORD,
        "",
        [mock_type],
        "1",
        action,
        "ALL",
    )
    pytest.raises(
        Exception, lambda: mocks.export_to_vault(app, action, config)
    )


def test_redact_register():
    content = {
        consts.MockType.HTTP: {
            "actions": {"action_id_1": {"param_1": [{"password": "123"}]}}
        }
    }

    reg1 = MocksRegister.from_dict(content.copy())

    content[consts.MockType.HTTP]["actions"]["action_id_1"]["param_1"][0][
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
