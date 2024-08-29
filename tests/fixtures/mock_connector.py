from unittest.mock import MagicMock
from uuid import uuid4

import requests

from soar_asset_mocker import AssetMocker, MockType


class MockConnector:
    container_id = str(uuid4())
    action_id = str(uuid4())
    asset_id = str(uuid4())
    app_run_id = str(uuid4())
    app_name_uid = str(uuid4())

    def __init__(self, config) -> None:
        self.config = config

    @AssetMocker.use(MockType.HTTP)
    def example_connector_action(self, param):
        return requests.get(param.get("url")).text

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
