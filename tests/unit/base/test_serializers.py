from io import BytesIO

import pytest

from soar_asset_mocker.base.serializers import decode_unserializable_types, encode_unserializable_types


@pytest.mark.parametrize("content", [BytesIO(bytes(1)), "text"])
def test_encode_decode(content):
    binary = encode_unserializable_types(content)
    decoded = decode_unserializable_types(binary)
    if isinstance(content, BytesIO):
        assert decoded.getvalue() == content.getvalue()
    else:
        assert decoded == content
