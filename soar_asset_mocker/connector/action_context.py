from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

from soar_asset_mocker.utils.redactor import redact_nested
from soar_asset_mocker.connector import soar_api


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

    @classmethod
    def from_action_run(cls, app, param):
        action_run = soar_api.get_action_run(app, app._BaseConnector__action_run_id)
        run_id = action_run.get("playbook_run")
        playbook_run = soar_api.get_playbook_run(app, run_id)
        playbook = soar_api.get_playbook(app, playbook_run.get("playbook"))
        return ActionContext(
            id=app.get_action_identifier(),
            params=deepcopy(param),
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
        return str(sorted([str(value) for key, value in redact_nested(self.params).items() if key != "context"]))
