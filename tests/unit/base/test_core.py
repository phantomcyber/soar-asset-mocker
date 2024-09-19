from unittest.mock import patch

from yaml import dump

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.core import AssetMocker
from soar_asset_mocker.connector import ActionContext, AssetConfig


def get_decorated_method():
    @AssetMocker.use(MockType.HTTP)
    def connector_method(app, param): ...

    return connector_method


@patch("soar_asset_mocker.base.core.RecordOrchestrator")
def test_record_scenario(orchestrator, app_config, app_mock):
    app_config["am_mode"] = "RECORD"
    method = get_decorated_method()
    app, server = app_mock
    app.get_config.return_value = app_config

    method(app, {})

    app.save_progress.assert_called_once_with(
        "[Asset Mocker] Recording to container 1234, used mockers: http"
    )
    orchestrator.record.assert_called_once_with(
        app,
        AssetConfig("app_1234", "RECORD", "", {"http"}, "1234"),
        ActionContext("1234", {}, "1234", "1234"),
    )


@patch("soar_asset_mocker.base.core.MockOrchestrator")
def test_mock_scenario(orchestrator, app_mock, app_config):
    method = get_decorated_method()
    file_content = dump({"http": {}})
    app_config["am_mode"] = "MOCK"
    app_config["am_file"] = file_content
    app, server = app_mock
    app.get_config.return_value = app_config

    method(app, {})

    app.save_progress.assert_called_once_with(
        "[Asset Mocker] Mocking, used mockers: http"
    )
    orchestrator.mock.assert_called_once_with(
        AssetConfig("app_1234", "MOCK", file_content, {"http"}, "1234"),
        ActionContext("1234", {}, "1234", "1234"),
    )


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
