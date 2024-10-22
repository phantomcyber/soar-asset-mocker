from soar_asset_mocker.connector.action_context import ActionContext


def test_action_from_action_run(app_mock, action_context):
    app, _ = app_mock
    action = ActionContext.from_action_run(app, {"param": 1})
    assert action_context == action


def test_action_from_action_run_failed_endpoints(app_mock, action_context):
    app, http = app_mock
    http.expect_request("/rest/action_run/action_run_id").respond_with_json({}, 500)
    http.expect_request("/rest/playbook_run/pb_id").respond_with_json({}, 500)
    action = ActionContext.from_action_run(app, {"param": 1})
    assert action_context == action
