import json

FIELDS_TO_REDACT = [
    "password",
    "confirm_password",
    "user_session_token",
    "originalTo",
    "originalFrom",
    "reporter",
    "token",
    "authorization",
    "bearer",
    "key",
    "secret",
]

REDACTED = "*****"


def redact_string(key: str, value):
    if any(field in key.lower() for field in FIELDS_TO_REDACT):
        return REDACTED
    return value


def redact_nested(data, path=""):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = redact_nested(value, f"{path}.{key}")
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = redact_nested(data[i], path)
    elif isinstance(data, str):
        try:
            return json.dumps(
                redact_nested(
                    json.loads(data),
                    path,
                )
            )
        except json.JSONDecodeError:
            return redact_string(path, data)
    elif isinstance(data, bytes):
        try:
            decoded = data.decode()
            redacted = redact_nested(decoded, path)
            return redacted.encode()
        except (UnicodeDecodeError, UnicodeEncodeError):
            return data
    return data
