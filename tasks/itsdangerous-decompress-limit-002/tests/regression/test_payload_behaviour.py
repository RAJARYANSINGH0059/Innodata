"""Pre-existing behaviour that must hold in every state."""
import pytest

from itsdangerous import BadPayload
from itsdangerous.encoding import base64_encode
from itsdangerous.url_safe import URLSafeSerializer, URLSafeTimedSerializer

KEY = "secret"


def test_roundtrip_compressed_and_uncompressed():
    s = URLSafeSerializer(KEY)
    assert s.loads(s.dumps("0" * 50_000)) == "0" * 50_000
    assert s.loads(s.dumps({"a": 1})) == {"a": 1}
    t = URLSafeTimedSerializer(KEY)
    assert t.loads(t.dumps([1, 2, 3])) == [1, 2, 3]


def test_corrupt_zlib_is_bad_payload():
    s = URLSafeSerializer(KEY)
    payload = b"." + base64_encode(b"not zlib data at all")
    signed = s.make_signer(s.salt).sign(payload).decode()
    with pytest.raises(BadPayload):
        s.loads(signed)


def test_instances_are_independent():
    a, b = URLSafeSerializer(KEY), URLSafeSerializer(KEY)
    a.max_decompressed_size = 10
    assert b.loads(b.dumps("0" * 5000)) == "0" * 5000

def test_uncompressed_payload_unaffected():  # AC5 (preservation)
    s = URLSafeSerializer(KEY)
    s.max_decompressed_size = 1
    tok = s.dumps({"a": 1})
    assert not tok.startswith(".") and "." in tok
    assert s.loads(tok) == {"a": 1}


def test_corrupt_zlib_still_bad_payload_with_limit():  # AC8 (preservation)
    s = URLSafeSerializer(KEY)
    s.max_decompressed_size = 10_000
    # ".": compressed marker, base64 of bytes that are not zlib data, validly signed via the signer
    payload = b"." + base64_encode(b"not zlib data at all")
    signed = s.make_signer(s.salt).sign(payload).decode()
    with pytest.raises(BadPayload):
        s.loads(signed)
