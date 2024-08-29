from soar_asset_mocker.connector import soar_libs
from tests.fixtures.mock_connector import MockConnector
from tests.fixtures.mock_create_attachment import AttachmentHolder


def test_record_and_mock(http_url_expect_text):
    url, expected_text = http_url_expect_text
    holder = AttachmentHolder()
    soar_libs.Vault.create_attachment = holder.create_attachment
    soar_libs.phantom.APP_SUCCESS = True
    soar_libs.phantom.APP_JSON_HASH = "hash"

    connector = MockConnector(
        {"am_mode": "RECORD", "directory": MockConnector.app_name_uid}
    )

    assert connector.example_connector_action({"url": url}) == expected_text

    connector.config["am_mode"] = "MOCK"
    connector.config["am_file"] = holder.attachments[0]
    print(holder.attachments[-1])

    assert connector.example_connector_action({"url": url}) == expected_text


def test_mock_without_recording():
    # TODO
    ...
