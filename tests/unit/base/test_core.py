from unittest.mock import patch

from yaml import dump

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.core import AssetMocker
from soar_asset_mocker.connector import ActionContext, AssetConfig
from tests.fixtures.connector import get_app_config, get_app_mock


def get_decorated_method():
    @AssetMocker.wrap((MockType.HTTP))
    def connector_method(app, param): ...

    return connector_method


@patch("soar_asset_mocker.base.core.RecordOrchestrator")
def test_record_scenario(orchestrator):
    method = get_decorated_method()
    app = get_app_mock(get_app_config(mode="RECORD"))

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
def test_mock_scenario(orchestrator):
    method = get_decorated_method()
    file_content = dump({"http": {}})
    app = get_app_mock(get_app_config(mode="MOCK", file_content=file_content))

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
def test_do_nothing_scenario(record_orch, mock_orch):
    method = get_decorated_method()
    app = get_app_mock(get_app_config(mode="NONE", file_content=dump({})))

    method(app, {})

    app.save_progress.assert_not_called()
    record_orch.assert_not_called()
    mock_orch.assert_not_called()
