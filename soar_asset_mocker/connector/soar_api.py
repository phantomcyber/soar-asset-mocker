import requests


def parse_response(app, response: requests.Response):
    if response.status_code != 200:
        app.debug_print(f"Called {response.url} failed.\nStatus: {response.status_code}.\nMessage:{response.text}")
        return {}
    return response.json()


def get_playbook(app, playbook_id):
    base_url = app.get_phantom_base_url()
    r = requests.get(f"{base_url}/rest/playbook/{playbook_id}", verify=False)
    return parse_response(app, r)


def get_playbook_run(app, run_id):
    base_url = app.get_phantom_base_url()
    r = requests.get(f"{base_url}/rest/playbook_run/{run_id}", verify=False)
    return parse_response(app, r)


def get_action_run(app, action_id):
    base_url = app.get_phantom_base_url()
    r = requests.get(f"{base_url}/rest/action_run/{action_id}", verify=False)
    return parse_response(app, r)
