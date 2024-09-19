from unittest.mock import MagicMock, patch

import pytest

from soar_asset_mocker.http.http_mocker import HTTPMocker
from soar_asset_mocker.mocker.mocker_orchestrator import MockOrchestrator


@patch(
    "soar_asset_mocker.mocker.mocker_orchestrator.MockOrchestrator.mockers_from_config"
)
@patch("soar_asset_mocker.mocker.mocker_orchestrator.MocksRegister")
def test_orchestrator_mock(
    register, from_config, asset_config, action_context
):
    http_mocker = MagicMock()
    from_config.return_value = [http_mocker]
    asset_config.mode = "MOCK"

    with MockOrchestrator.mock(asset_config, action_context):
        ...

    http_mocker.mock.assert_called_once()


def test_mockers_from_config(asset_config):
    asset_config.mode = "MOCK"
    mockers = MockOrchestrator.mockers_from_config(asset_config)
    assert isinstance(mockers[0], HTTPMocker)


def test_mockers_from_config_fail(asset_config):
    asset_config.mock_types = {"MISSING_TYPE"}
    pytest.raises(
        KeyError,
        lambda: MockOrchestrator.mockers_from_config(asset_config),
    )
