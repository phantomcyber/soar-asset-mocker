from unittest.mock import MagicMock

import pytest

from soar_asset_mocker.base.consts import AssetMockerScope, MockType
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.connector.asset_config import AssetConfig


@pytest.fixture(name="mock_register")
def http_mock_register():
    return MocksRegister.from_dict({"register": {MockType.HTTP.value: {"actions": {"action_id_1": {"param_1": [1, 2, 3]}}}}})


@pytest.fixture
def http_url_expect_text(httpserver):
    endpoint = "/ping"
    expected_text = "healthcheck"
    httpserver.expect_request(endpoint).respond_with_data(expected_text)
    return httpserver.url_for(endpoint), expected_text


@pytest.fixture
def action_context():
    return ActionContext(
        id="action_id",
        params={"param": 1},
        app_run_id="run_1",
        asset_id="asset_1",
        action_run_id="action_run_id",
        playbook_run_id="pb_run_id",
        name="action",
    )


@pytest.fixture
def asset_config(action_context):
    return AssetConfig(
        app_name_uid="app_1234",
        mode="MOCK",
        mock_file="",
        mock_types={MockType.HTTP},
        container_id="1",
        scope=AssetMockerScope.ALL,
    )


@pytest.fixture
def app_config(
    directory="app_1234",
    mock_types=[],
    mode="NONE",
    file_content="",
    container_id="1",
    scope=AssetMockerScope.ALL,
):
    return {
        "directory": directory,
        "am_mock_types": mock_types,
        "am_mode": mode,
        "am_file": file_content,
        "am_scope": scope,
        "am_container_id": container_id,
    }


@pytest.fixture
def app_mock(httpserver, asset_config, action_context):
    app = MagicMock(name="app")
    app.get_config = MagicMock(return_value={})
    app.save_artifact = MagicMock(return_value=(None, None, None))
    app._BaseConnector__action_run_id = action_context.action_run_id
    app.save_progress = MagicMock()
    results = MagicMock()
    app.get_action_results = MagicMock(return_value=results)
    app.get_container_id = MagicMock(return_value=asset_config.container_id)
    app.get_action_identifier = MagicMock(return_value=action_context.id)
    app.get_app_run_id = MagicMock(return_value=action_context.app_run_id)
    app.get_asset_id = MagicMock(return_value=action_context.asset_id)
    app.get_phantom_base_url = MagicMock(return_value=httpserver.url_for(""))
    httpserver.expect_request("/rest/action_run/action_run_id").respond_with_json({"id": "action_run_id", "playbook_run": "pb_run_id"})
    httpserver.expect_request("/rest/playbook_run/pb_run_id").respond_with_json({"playbook": "pb_id", "test_mode": False})
    httpserver.expect_request("/rest/playbook/pb_id").respond_with_json({})
    app.get_action_name = MagicMock(return_value=action_context.name)
    return app, httpserver
