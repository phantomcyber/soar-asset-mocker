from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.mocker_orchestrator import MockOrchestrator


@patch(
    "soar_asset_mocker.mocker.mocker_orchestrator.MockOrchestrator.mockers_from_config"
)
@patch("soar_asset_mocker.mocker.mocker_orchestrator.MocksRegister")
def test_orchestrator_record(mocks_register, from_config):
    action = ActionContext("id", {"param": 1}, "run_1", "asset_1")
    config = AssetConfig("", "RECORD", "", [MockType.HTTP], "")
    http_mocker = MagicMock()
    from_config.return_value = [http_mocker]

    with MockOrchestrator.mock(config, action):
        ...

    http_mocker.mock.assert_called_once()


def test_mockers_from_config():
    mockers = MockOrchestrator.mockers_from_config(
        AssetConfig("", "RECORD", "", {MockType.HTTP}, "")
    )
    assert isinstance(mockers[0], HTTPMocker)


def test_mockers_from_config_fail():
    pytest.raises(
        KeyError,
        lambda: MockOrchestrator.mockers_from_config(
            AssetConfig("", "RECORD", "", {"MISSING_TYPE"}, "")
        ),
    )
