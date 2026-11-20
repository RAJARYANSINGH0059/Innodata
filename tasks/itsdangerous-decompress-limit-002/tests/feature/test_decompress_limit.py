"""Feature tests for max_decompressed_size. Written from instruction.md only."""
import tracemalloc

import pytest

from itsdangerous import BadPayload
from itsdangerous.url_safe import URLSafeSerializer, URLSafeTimedSerializer

KEY = "secret"


def json_len(n):
    """Compact-JSON length of the string "0"*n (two quotes added)."""
    return n + 2


@pytest.mark.parametrize("cls", [URLSafeSerializer, URLSafeTimedSerializer])
def test_oversized_compressed_payload_rejected(cls):  # AC1
    s = cls(KEY)
    tok = s.dumps("0" * (1 << 20))
    s.max_decompressed_size = 1024
    with pytest.raises(BadPayload):
        s.loads(tok)


def test_exact_size_boundary():  # AC2
    n = 5000
    s = URLSafeSerializer(KEY)
    tok = s.dumps("0" * n)
    s.max_decompressed_size = json_len(n)
    assert s.loads(tok) == "0" * n
    s.max_decompressed_size = json_len(n) - 1
    with pytest.raises(BadPayload):
        s.loads(tok)


def test_default_is_none_and_unlimited():  # AC3
    assert URLSafeSerializer.max_decompressed_size is None
    assert URLSafeTimedSerializer.max_decompressed_size is None
    s = URLSafeSerializer(KEY)
    assert s.loads(s.dumps("0" * (1 << 20))) == "0" * (1 << 20)


def test_rejection_does_not_materialise_full_output():  # AC4
    s = URLSafeSerializer(KEY)
    tok = s.dumps("0" * (32 << 20))  # ~32 MiB when decompressed, tiny token
    s.max_decompressed_size = 1024
    tracemalloc.start()
    try:
        with pytest.raises(BadPayload):
            s.loads(tok)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 4 << 20, f"peak {peak} bytes: output was materialised"




def test_loads_unsafe_oversized_invalid_signature():  # AC6
    s = URLSafeSerializer(KEY)
    other = URLSafeSerializer("different-key")
    s.max_decompressed_size = 1024
    sig_bad = other.dumps("0" * (1 << 20))  # valid under another key => invalid signature here
    assert s.loads_unsafe(sig_bad) == (False, None)


def test_subclass_and_instance_configuration():  # AC7
    class Limited(URLSafeSerializer):
        max_decompressed_size = 100

    tok = URLSafeSerializer(KEY).dumps("0" * 10_000)
    with pytest.raises(BadPayload):
        Limited(KEY).loads(tok)
    inst = URLSafeSerializer(KEY)
    inst.max_decompressed_size = 100
    with pytest.raises(BadPayload):
        inst.loads(tok)


def test_zero_limit_rejects_any_compressed_payload():  # AC2 with N = 0 (0 is a limit, not "unset")
    s = URLSafeSerializer(KEY)
    tok = s.dumps("0" * 5000)
    s.max_decompressed_size = 0
    with pytest.raises(BadPayload):
        s.loads(tok)
