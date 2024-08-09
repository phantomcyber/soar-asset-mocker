from dataclasses import dataclass

from soar_asset_mocker.utils.redactor import redact_nested


@dataclass
class ActionContext:
    id: str
    params: dict
    app_run_id: str
    asset_id: str

    @classmethod
    def from_action_run(cls, app, param):
        return ActionContext(
            id=app.get_action_identifier(),
            params=param,
            app_run_id=app.get_app_run_id(),
            asset_id=app.get_asset_id(),
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
