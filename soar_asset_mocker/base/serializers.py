from io import BytesIO
from typing import Any


def decode_unserializable_types(obj: Any):
    if "__BytesIO__" in obj:
        obj = BytesIO(obj["as_bytes"])
    return obj


def encode_unserializable_types(obj: Any):
    if isinstance(obj, BytesIO):
        return {"__BytesIO__": True, "as_bytes": obj.getvalue()}
    return obj
