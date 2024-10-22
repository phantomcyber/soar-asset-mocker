from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.recorder_orchestrator import RecordOrchestrator


@patch("soar_asset_mocker.mocker.recorder_orchestrator.RecordOrchestrator.recorders_from_config")
@patch("soar_asset_mocker.mocker.recorder_orchestrator.MocksRegister")
def test_orchestrator_record(mocks_register, from_config, asset_config, action_context):
    http_mocker = MagicMock()
    from_config.return_value = [http_mocker]

    with RecordOrchestrator.record(None, asset_config, action_context):
        ...

    mocks_register().export_to_vault.assert_called_once_with(None, action_context, asset_config)
    http_mocker.record.assert_called_once()


def test_recorders_from_config(asset_config):
    asset_config.mode = "RECORD"
    recorders = RecordOrchestrator.recorders_from_config(asset_config)
    assert isinstance(recorders[0], HTTPMocker)


def test_recorders_from_config_fail(asset_config):
    asset_config.mock_types = {"MISSING_TYPE"}
    pytest.raises(
        KeyError,
        lambda: RecordOrchestrator.recorders_from_config(asset_config),
    )
