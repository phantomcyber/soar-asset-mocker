import pytest

from soar_asset_mocker.connector.asset_config import AssetConfig
from soar_asset_mocker.connector.soar_libs import vault_info


def test_asset_config_from_env(app_mock, asset_config, monkeypatch):
    app, http = app_mock
    app.get_config.return_value = {"directory": "app_1234"}

    asset_config.mock_types = set()
    asset_config.scope = "ALL"
    asset_config.mode = "RECORD"

    monkeypatch.setenv("SOAR_AM_ARTIFACT_ID", "1")
    monkeypatch.setenv("SOAR_AM_SCOPE", "ALL")
    monkeypatch.setenv("SOAR_AM_MODE", "RECORD")
    monkeypatch.setenv("SOAR_AM_CONTAINER_ID", "1")

    assert AssetConfig.from_app(app) == asset_config


@pytest.mark.parametrize("container_id", ["", "a", "1"])
def test_asset_config_from_env_load_artifact(container_id, app_mock, asset_config, monkeypatch, tmp_path):
    filename = "abc.msgpack"
    content = bytes(123)
    asset_config.mock_file = content
    with open(tmp_path / filename, "wb") as f:
        f.write(content)
    app, http = app_mock
    app.get_config.return_value = {"directory": "app_1234"}
    vault_info.return_value = (
        True,
        "",
        [{"name": "recording_1", "path": tmp_path / filename}],
    )

    asset_config.mock_types = set()
    asset_config.scope = "ALL"
    asset_config.mode = "MOCK"
    monkeypatch.setenv("SOAR_AM_FILE_NAME", "abc.msgpack")
    monkeypatch.setenv("SOAR_AM_FILE_CONTAINER_ID", container_id)
    monkeypatch.setenv("SOAR_AM_FILE_VAULT_ID", "abc.msgpack")
    monkeypatch.setenv("SOAR_AM_SCOPE", "ALL")
    monkeypatch.setenv("SOAR_AM_MODE", "MOCK")
    monkeypatch.setenv("SOAR_AM_CONTAINER_ID", "1")

    assert AssetConfig.from_app(app) == asset_config


def test_asset_config_from_env_no_artifact(app_mock, asset_config, monkeypatch):
    app, http = app_mock
    app.get_config.return_value = {"directory": "app_1234"}
    asset_config.mock_types = set()
    asset_config.scope = "ALL"
    asset_config.mode = "MOCK"
    monkeypatch.setenv("SOAR_AM_SCOPE", "ALL")
    monkeypatch.setenv("SOAR_AM_MODE", "MOCK")
    monkeypatch.setenv("SOAR_AM_CONTAINER_ID", "1")

    assert AssetConfig.from_app(app) == asset_config


def test_asset_config_from_env_artifact_fail(app_mock, asset_config, monkeypatch):
    app, http = app_mock
    app.get_config.return_value = {"directory": "app_1234"}
    asset_config.mock_types = set()
    asset_config.scope = "ALL"
    asset_config.mode = "MOCK"
    vault_info.return_value = (
        False,
        "",
        {},
    )
    monkeypatch.setenv("SOAR_AM_FILE_NAME", "a.msgpack")
    monkeypatch.setenv("SOAR_AM_SCOPE", "ALL")
    monkeypatch.setenv("SOAR_AM_MODE", "MOCK")
    monkeypatch.setenv("SOAR_AM_CONTAINER_ID", "1")

    assert AssetConfig.from_app(app) == asset_config


def test_asset_config_from_asset_settings(app_mock, asset_config, app_config):
    app, http = app_mock
    asset_config.mock_types = set()
    app_config["am_mode"] = "MOCK"
    app.get_config.return_value = app_config
    assert AssetConfig.from_app(app) == asset_config
