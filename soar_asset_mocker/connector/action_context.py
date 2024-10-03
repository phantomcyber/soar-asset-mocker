from dataclasses import dataclass
from typing import Optional

import requests

from soar_asset_mocker.utils.redactor import redact_nested


@dataclass
class ActionContext:
    id: str
    params: dict
    app_run_id: str
    asset_id: str
    action_run_id: str
    playbook_run_id: Optional[str] = None
    vpe_test_mode: bool = False
    playbook_name: str = ""
    name: str = ""

    @staticmethod
    def _get_playbook(app, playbook_id):
        base_url = app.get_phantom_base_url()
        endpoint = f"{base_url}/rest/playbook/{playbook_id}"
        r = requests.get(endpoint, verify=False)
        if r.status_code != 200:
            return {}
        return r.json()

    @staticmethod
    def _get_playbook_run(app, run_id):
        base_url = app.get_phantom_base_url()
        endpoint = f"{base_url}/rest/playbook_run/{run_id}"
        r = requests.get(endpoint, verify=False)
        if r.status_code != 200:
            return {}
        return r.json()

    @staticmethod
    def _get_action_run(app, action_id):
        base_url = app.get_phantom_base_url()
        endpoint = f"{base_url}/rest/action_run/{action_id}"
        print(endpoint)
        r = requests.get(endpoint, verify=False)
        if r.status_code != 200:
            return {}
        return r.json()

    @classmethod
    def from_action_run(cls, app, param):
        action_run = cls._get_action_run(
            app, app._BaseConnector__action_run_id
        )
        run_id = action_run.get("playbook_run")
        playbook_run = cls._get_playbook_run(app, run_id)
        playbook = cls._get_playbook(app, playbook_run.get("playbook"))
        return ActionContext(
            id=app.get_action_identifier(),
            params=param,
            app_run_id=app.get_app_run_id(),
            action_run_id=action_run.get("id"),
            playbook_run_id=run_id,
            asset_id=app.get_asset_id(),
            vpe_test_mode=playbook_run.get("test_mode", False),
            playbook_name=playbook.get("name", ""),
            name=app.get_action_name(),
        )

    @property
    def params_key(self):
        return str(
            sorted(
                [
                    str(value)
                    for key, value in redact_nested(self.params).items()
                    if key != "context"
                ]
            )
        )
