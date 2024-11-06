import msgpack
from typer.testing import CliRunner

from soar_asset_mocker.cli.app import cli_app

runner = CliRunner()


def test_fetch(tmp_path, httpserver):
    container_id = "1"
    hash_value = "1234"
    vault_doc = "1234"
    path = str(tmp_path / "tmp.yaml")
    httpserver.expect_request(
        f"/rest/container/{container_id}/attachments",
        query_string="sort=create_time&order=desc&page=0&page_size=500&pretty=true",
    ).respond_with_json(
        {
            "data": [
                {
                    "name": "1",
                    "create_time": "00:00 01.01.1990",
                    "vault_document": vault_doc,
                    "_pretty_metadata": {
                        "action_run_id": "3",
                        "asset_mocker_scope": "VPE",
                        "asset_mocker_version": "0.1.0",
                        "playbook_name": "pb_1",
                        "playbook_run_id": "1",
                        "app_name": "abc",
                    },
                },
                {
                    "name": "2",
                    "create_time": "00:00 01.01.1990",
                    "vault_document": vault_doc,
                    "_pretty_metadata": {
                        "action_run_id": "1",
                        "asset_mocker_scope": "VPE",
                        "asset_mocker_version": "0.1.0",
                        "app_name": "abc",
                    },
                },
                {
                    "name": "3",
                    "create_time": "00:00 01.01.1990",
                    "vault_document": vault_doc,
                    "_pretty_metadata": {
                        "action_run_id": "2",
                        "asset_mocker_scope": "VPE",
                        "asset_mocker_version": "0.1.0",
                        "app_name": "abc",
                    },
                },
            ]
        }
    )
    httpserver.expect_request(f"/rest/vault_document/{vault_doc}").respond_with_json({"hash": hash_value})
    httpserver.expect_request("/rest/download_attachment", query_string=f"vault_id={hash_value}").respond_with_data(
        msgpack.packb({"register": [{"request": {"hash": hash_value}}]})
    )

    result = runner.invoke(
        cli_app,
        [
            "fetch",
            container_id,
            path,
            "--phantom-url",
            httpserver.url_for(""),
        ],
        input="admin\npassword\n0,1\n0\n",
    )
    assert result.exit_code == 0, f"out:{result.output}\nexc:{result.exception}"
    with open(path, "rb") as f:
        assert msgpack.unpackb(f.read()) == {
            "register": [
                {"request": {"hash": hash_value}},
                {"request": {"hash": hash_value}},
                {"request": {"hash": hash_value}},
            ]
        }


def test_fetch_no_attachments(tmp_path, httpserver):
    container_id = "1"
    httpserver.expect_request(
        f"/rest/container/{container_id}/attachments",
        query_string="sort=create_time&order=desc&page=0&page_size=500&pretty=true",
    ).respond_with_json({})

    result = runner.invoke(
        cli_app,
        [
            "fetch",
            container_id,
            str(tmp_path / "tmp.yaml"),
            "--phantom-url",
            httpserver.url_for(""),
        ],
        input="admin\npassword\n0-2\n",
    )
    assert result.exit_code == 2, result.output
