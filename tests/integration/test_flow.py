from unittest.mock import MagicMock
from uuid import uuid4

import requests

from soar_asset_mocker import AssetMocker, MockType
from tests.fixtures.mock_phantom import phantom_module


class MockConnector:
    container_id = str(uuid4())
    action_id = str(uuid4())
    asset_id = str(uuid4())
    app_run_id = str(uuid4())
    app_name_uid = str(uuid4())

    def __init__(self, config) -> None:
        self.config = config

    def get_app_run_id(self):
        return self.get_app_run_id

    def get_action_results(self):
        return [MagicMock()]

    def save_progress(self, text):
        return

    def save_artifact(self, text):
        return True, "ok", None

    def get_action_identifier(self):
        return self.action_id

    def get_asset_id(self):
        return self.container_id

    def get_container_id(self):
        return self.container_id

    def get_config(self):
        return self.config

    @AssetMocker.use(MockType.HTTP)
    def example_connector_action(self, param):
        return requests.get(param.get("url")).text


class AttachmentHolder:

    def __init__(self) -> None:
        self.attachments = []

    def create_attachment(self, body, file_name, container_id):
        self.attachments.append(body)
        return {"hash": str(uuid4()), "succeeded": True}


def test_record_and_mock(http_url_expect_text):
    url, expected_text = http_url_expect_text
    holder = AttachmentHolder()
    phantom_module.Vault.create_attachment = holder.create_attachment
    phantom_module.phantom.APP_SUCCESS = True
    phantom_module.phantom.APP_JSON_HASH = "hash"

    connector = MockConnector(
        {"am_mode": "RECORD", "directory": MockConnector.app_name_uid}
    )

    assert connector.example_connector_action({"url": url}) == expected_text

    connector.config["am_mode"] = "MOCK"
    connector.config["am_file"] = holder.attachments[0]
    print(holder.attachments[-1])

    assert connector.example_connector_action({"url": url}) == expected_text
