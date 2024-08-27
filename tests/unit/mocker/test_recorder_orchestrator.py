from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.recorder_orchestrator import RecordOrchestrator


@patch(
    "soar_asset_mocker.mocker.recorder_orchestrator.RecordOrchestrator.recorders_from_config"
)
@patch("soar_asset_mocker.mocker.recorder_orchestrator.MocksRegister")
def test_orchestrator_record(mocks_register, from_config):
    action = ActionContext("id", {"param": 1}, "run_1", "asset_1")
    config = AssetConfig("", "RECORD", "", [MockType.HTTP], "")
    http_mocker = MagicMock()
    from_config.return_value = [http_mocker]

    with RecordOrchestrator.record(None, config, action):
        ...

    mocks_register().export_to_vault.assert_called_once_with(
        None, action, config
    )
    http_mocker.record.assert_called_once()


def test_recorders_from_config():
    recorders = RecordOrchestrator.recorders_from_config(
        AssetConfig("", "RECORD", "", {MockType.HTTP}, "")
    )
    assert isinstance(recorders[0], HTTPMocker)


def test_recorders_from_config_fail():
    pytest.raises(
        KeyError,
        lambda: RecordOrchestrator.recorders_from_config(
            AssetConfig("", "RECORD", "", {"MISSING_TYPE"}, "")
        ),
    )
