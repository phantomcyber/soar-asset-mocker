import pytest
import requests

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.exceptions import MissingRecordingException
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.http.http_mocker import HTTPMocker


def http_call(url):
    return requests.get(url).text


def test_http_record_and_mock(http_url_expect_text, action_context):

    url, expected_text = http_url_expect_text
    register = MocksRegister()

    with HTTPMocker().record(register, action_context):
        assert http_call(url) == expected_text

    recordings = register.get_mock_recordings(MockType.HTTP, action_context)

    assert len(recordings) == 1

    assert list(recordings[0].keys()) == ["request", "response"]

    with HTTPMocker().mock(register, action_context):
        assert http_call(url) == expected_text


def test_http_mock_without_recording(http_url_expect_text, action_context):
    url, expected_text = http_url_expect_text
    register = MocksRegister()

    def mocking_without_recording():
        with HTTPMocker().mock(register, action_context):
            http_call(url) == expected_text

    pytest.raises(MissingRecordingException, mocking_without_recording)
