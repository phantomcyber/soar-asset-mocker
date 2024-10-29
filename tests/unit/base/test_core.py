from unittest.mock import patch

from yaml import dump

from soar_asset_mocker.base.consts import AssetMockerMode, MockType
from soar_asset_mocker.base.core import AssetMocker


def get_decorated_method():
    @AssetMocker.use(MockType.HTTP)
    def connector_method(app, param): ...

    return connector_method


@patch("soar_asset_mocker.base.core.MockOrchestrator")
def test_mock_scenario(orchestrator, app_mock, app_config, asset_config, action_context):
    method = get_decorated_method()
    file_content = dump({"http": {}})
    app_config["am_mode"] = asset_config.mode
    asset_config.mode = AssetMockerMode.MOCK
    app_config["am_file"] = file_content
    asset_config.mock_file = file_content
    app, server = app_mock
    app.get_config.return_value = app_config

    method(app, action_context.params)

    app.save_progress.assert_called_once_with("[Asset Mocker] Mocking, used mockers: http")
    orchestrator.mock.assert_called_once_with(asset_config, action_context)


@patch("soar_asset_mocker.base.core.RecordOrchestrator")
@patch("soar_asset_mocker.base.core.MockOrchestrator")
def test_do_nothing_scenario(record_orch, mock_orch, app_mock, app_config):
    app_config["am_mode"] = "NONE"
    app, server = app_mock
    app.get_config.return_value = app_config
    method = get_decorated_method()
    method(app, {})

    app.save_progress.assert_not_called()
    record_orch.assert_not_called()
    mock_orch.assert_not_called()


@patch("soar_asset_mocker.base.core.MockOrchestrator")
def test_no_app_results(orchestrator, app_mock, app_config, asset_config, action_context):
    method = get_decorated_method()
    file_content = dump({"http": {}})
    app_config["am_mode"] = asset_config.mode
    asset_config.mode = AssetMockerMode.MOCK
    app_config["am_file"] = file_content
    asset_config.mock_file = file_content
    app, server = app_mock
    app.get_config.return_value = app_config
    app.get_action_results.return_value = []

    method(app, action_context.params)

    app.save_progress.assert_called_once_with("[Asset Mocker] Mocking, used mockers: http")
    orchestrator.mock.assert_called_once_with(asset_config, action_context)
