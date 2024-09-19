from unittest.mock import MagicMock

import pytest

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig


@pytest.fixture
def http_url_expect_text(httpserver):
    endpoint = "/ping"
    expected_text = "healthcheck"
    httpserver.expect_request(endpoint).respond_with_data(expected_text)
    return httpserver.url_for(endpoint), expected_text


@pytest.fixture
def action_context():
    return ActionContext(
        "action_id", {"param": 1}, "run_1", "asset_1", "action_run_id"
    )


@pytest.fixture
def asset_config(action_context):
    return AssetConfig(
        "app_1234", "MOCK", "", [MockType.HTTP], "1", action_context, "ALL"
    )


@pytest.fixture
def app_config(
    directory="app_1234",
    mock_types=[],
    mode="NONE",
    file_content="",
    container_id="id_1234",
):
    return {
        "directory": directory,
        "am_mock_types": mock_types,
        "am_mode": mode,
        "am_file": file_content,
        "container_id": container_id,
    }


@pytest.fixture
def app_mock(httpserver):
    app = MagicMock(name="app")
    app.get_config = MagicMock(return_value={})
    app.save_artifact = MagicMock(return_value=(None, None, None))
    app.save_progress = MagicMock()
    results = MagicMock()
    app.get_action_results = MagicMock(return_value=results)
    app.get_container_id = MagicMock(return_value="1234")
    app.get_action_identifier = MagicMock(return_value="1234")
    app.get_app_run_id = MagicMock(return_value="1234")
    app.get_asset_id = MagicMock(return_value="1234")
    app.get_phantom_base_url = MagicMock(return_value=httpserver.url_for(""))
    return app, httpserver
