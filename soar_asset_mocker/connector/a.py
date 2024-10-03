{
    "id": 45,
    "action_exec": [],
    "cancelled": None,
    "container": 8,
    "ip_address": "10.56.155.125",
    "log_level": 1,
    "message": "Starting playbook 'local/phantom_microsoft_windows_remote_management (id: 159, version: 1, pyversion: 3, scm id: 2)' on event '8' with playbook run id: 45, running as user '1'",
    "owner": 1,
    "playbook": 159,
    "start_time": "2024-10-01T09: 05: 01.160000Z",
    "status": "running",
    "scope": "new",
    "test_mode": True,
    "update_time": "2024-10-01T09: 05: 19.431063Z",
    "last_artifact": 158,
    "misc": {
        "scope": "new",
        "callback": {
            "block_ip_1": {
                "action": "block ip",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_24",
                "loop_state": "",
            },
            "get_file_2": {
                "action": "get file",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "upload_file_1",
                "loop_state": "",
            },
            "copy_file_1": {
                "action": "copy file",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_2",
                "loop_state": "",
            },
            "run_script_1": {
                "action": "run script",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_18",
                "loop_state": "",
            },
            "logoff_user_1": {
                "action": "logoff user",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_13",
                "loop_state": "",
            },
            "run_command_1": {
                "action": "run command",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_16",
                "loop_state": "",
            },
            "run_command_2": {
                "action": "run command",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_25",
                "loop_state": "",
            },
            "upload_file_1": {
                "action": "upload file",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_1",
                "loop_state": "",
            },
            "list_policies_1": {
                "action": "list policies",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_6",
                "loop_state": "",
            },
            "list_sessions_1": {
                "action": "list sessions",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_12",
                "loop_state": "",
            },
            "list_processes_1": {
                "action": "list processes",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_15",
                "loop_state": "",
            },
            "block_file_path_1": {
                "action": "block file path",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_5",
                "loop_state": "",
            },
            "list_connections_1": {
                "action": "list connections",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_14",
                "loop_state": "",
            },
            "add_firewall_rule_1": {
                "action": "add firewall rule",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_21",
                "loop_state": "",
            },
            "terminate_process_1": {
                "action": "terminate process",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_17",
                "loop_state": "",
            },
            "activate_partition_1": {
                "action": "activate partition",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_10",
                "loop_state": "",
            },
            "list_firewall_rules_1": {
                "action": "list firewall rules",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_20",
                "loop_state": "",
            },
            "list_firewall_rules_2": {
                "action": "list firewall rules",
                "cb_called": "no",
                "cb_result": False,
                "cb_fn_name": "filter_22",
                "loop_state": "",
            },
            "deactivate_partition_1": {
                "action": "deactivate partition",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_11",
                "loop_state": "",
            },
            "restart_system_invalid": {
                "action": "restart system",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_8",
                "loop_state": "",
            },
            "shutdown_system_invalid": {
                "action": "shutdown system",
                "cb_called": "yes",
                "cb_result": True,
                "cb_fn_name": "filter_9",
                "loop_state": "",
            },
        },
        "dbg_token": "1727773497663",
        "parent_playbook_run": None,
    },
    "run_data": {},
    "version": 1,
    "effective_user": 1,
    "node_guid": "b76caee2-2385-4b02-9c24-bbdb9e3a99c6",
    "playbook_run_batch": None,
    "parent_run": None,
    "inputs": None,
    "outputs": None,
}
