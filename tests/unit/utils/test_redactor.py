import pytest

from soar_asset_mocker.utils.redactor import REDACTED, redact_nested, redact_string


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "confirm_password",
        "user_session_token",
        "originalTo",
        "originalFrom",
        "reporter",
        "token",
        "authorization",
        "bearer",
        "private-key",
        "public-key",
        "secret",
    ],
)
def test_redact_string(key):
    assert redact_string(key, "non-redacted") == REDACTED, key


def test_redact_skip_string():
    value = "non-redacted"
    assert redact_string("flag", "non-redacted") == value


@pytest.mark.parametrize(
    "input,output",
    [
        ({}, {}),
        ({"password": "redact"}, {"password": REDACTED}),
        ({"passwords": ["abc", "xyz"]}, {"passwords": [REDACTED, REDACTED]}),
        ('{"password":"abcd"}', f'{{"password": "{REDACTED}"}}'),
        (
            '{"password":"abcd"}'.encode(),
            f'{{"password": "{REDACTED}"}}'.encode(),
        ),
        ("{ab{", "{ab{"),
        (b"0\xbe", b"0\xbe"),
    ],
)
def test_redact_nested(input, output):
    assert redact_nested(input) == output
