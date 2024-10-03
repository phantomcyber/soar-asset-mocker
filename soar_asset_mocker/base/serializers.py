from io import BytesIO
from typing import Any


def decode_unserializable_types(obj: Any):
    obj = decode_bytesio(obj)
    return obj


def encode_unserializable_types(obj: Any):
    obj = encode_bytesio(obj)
    return obj


def decode_bytesio(obj):
    if "__BytesIO__" in obj:
        obj = BytesIO(obj["as_bytes"])
    return obj


def encode_bytesio(obj):
    if isinstance(obj, BytesIO):
        return {"__BytesIO__": True, "as_bytes": obj.getvalue()}
    return obj
