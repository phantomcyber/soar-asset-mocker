import yaml
from typer.testing import CliRunner

from soar_asset_mocker.cli.app import cli_app

runner = CliRunner()


def test_fetch(tmp_path, httpserver):
    container_id = "1"
    hash = "1234"
    vault_doc = "1234"
    path = str(tmp_path / "tmp.yaml")
    httpserver.expect_request(
        f"/rest/container/{container_id}/attachments",
        query_string="sort=create_time&order=desc&page=0&page_size=1000",
    ).respond_with_json(
        {
            "data": [
                {"name": "1", "vault_document": vault_doc},
                {"name": "2", "vault_document": vault_doc},
            ]
        }
    )
    httpserver.expect_request(
        f"/rest/vault_document/{vault_doc}"
    ).respond_with_json({"hash": hash})
    httpserver.expect_request(
        "/rest/download_attachment", query_string=f"vault_id={hash}"
    ).respond_with_json({"register": [{"request": {"hash": hash}}]})

    result = runner.invoke(
        cli_app,
        [
            "fetch",
            container_id,
            path,
            "--phantom-url",
            httpserver.url_for(""),
        ],
        input="admin\npassword\n0-3\n0-3\n",
    )
    assert result.exit_code == 0, result.output
    with open(path) as f:
        assert yaml.safe_load(f) == {
            "register": [
                {"request": {"hash": hash}},
                {"request": {"hash": hash}},
            ]
        }


def test_fetch_no_attachments(tmp_path, httpserver):
    container_id = "1"
    httpserver.expect_request(
        f"/rest/container/{container_id}/attachments",
        query_string="sort=create_time&order=desc&page=0&page_size=1000",
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
