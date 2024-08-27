import pytest
import requests

from soar_asset_mocker.base.consts import MockType
from soar_asset_mocker.base.exceptions import MissingRecordingException
from soar_asset_mocker.base.register import MocksRegister
from soar_asset_mocker.connector.action_context import ActionContext
from soar_asset_mocker.http.http_mocker import HTTPMocker


def http_call():
    return requests.get("https://1.1.1.1").text


def test_http_record_and_mock():
    action = ActionContext("", {}, "", "")
    register = MocksRegister()

    with HTTPMocker().record(register, action):
        real_call = http_call()

    recordings = register.get_mock_recordings(MockType.HTTP, action)

    assert len(recordings) > 0

    assert list(recordings[0].keys()) == ["request", "response"]

    with HTTPMocker().mock(register, action):
        assert real_call == http_call()


def test_http_mock_without_recording():
    action = ActionContext("", {}, "", "")
    register = MocksRegister()

    def mocking_without_recording():
        with HTTPMocker().mock(register, action):
            http_call()

    pytest.raises(MissingRecordingException, mocking_without_recording)
