import json

FIELDS_TO_REDACT = [
    "authorization",
    "bearer",
    "key",
    "originalTo",
    "originalFrom",
    "password",
    "reporter",
    "secret",
    "token",
]

REDACTED = "*ASSET_MOCKER_REDACTED*"

FIELDS_TO_REDACT_PAIRS = [(f, REDACTED) for f in FIELDS_TO_REDACT]


def redact_string(key: str, value):
    if any(field.lower() in key.lower() for field in FIELDS_TO_REDACT):
        return REDACTED
    return value


def update_nested_dict(mock_a, mock_b):
    for k, v in mock_b.items():
        if isinstance(v, dict):
            mock_a[k] = update_nested_dict(mock_a.get(k, {}), v)
        elif isinstance(v, list):
            mock_a[k] = [*mock_a.get(k, []), *v]
        else:
            mock_a[k] = v
    return mock_a


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
