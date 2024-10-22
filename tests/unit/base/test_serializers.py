from io import BytesIO

from soar_asset_mocker.base.serializers import decode_unserializable_types, encode_unserializable_types


def test_encode_decode_string():
    content = "text"
    binary = encode_unserializable_types(content)
    decoded = decode_unserializable_types(binary)
    assert decoded == content


def test_encode_decode_bytes():
    content = BytesIO(bytes(1))
    binary = encode_unserializable_types(content)
    decoded = decode_unserializable_types(binary)
    assert decoded.getvalue() == content.getvalue()
