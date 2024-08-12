from unittest.mock import MagicMock


def get_app_config(
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


def get_app_mock(get_config_retun):
    app = MagicMock(name="app")
    app.get_config = MagicMock(return_value=get_config_retun)
    app.save_artifact = MagicMock(return_value=(None, None, None))
    app.save_progress = MagicMock()
    results = MagicMock()
    app.get_action_results = MagicMock(return_value=results)
    app.get_container_id = MagicMock(return_value="1234")
    app.get_action_identifier = MagicMock(return_value="1234")
    app.get_app_run_id = MagicMock(return_value="1234")
    app.get_asset_id = MagicMock(return_value="1234")
    return app
