"""Feature tests for Serializer.needs_resign. Written from instruction.md only."""
import hashlib

import pytest
from freezegun import freeze_time

from itsdangerous import BadPayload, BadSignature, Serializer, TimedSerializer


def test_current_key_does_not_need_resign():  # AC1
    s = Serializer(["k1", "k2"])
    assert s.needs_resign(s.dumps({"a": 1})) is False


def test_older_keys_need_resign_three_key_rotation():  # AC2
    keys = ["k1", "k2", "k3"]
    s = Serializer(keys)
    tokens = {k: Serializer([k]).dumps(1) for k in keys}
    assert s.needs_resign(tokens["k3"]) is False
    assert s.needs_resign(tokens["k2"]) is True
    assert s.needs_resign(tokens["k1"]) is True


def test_fallback_signer_needs_resign_current_does_not():  # AC3
    old = Serializer("k", signer_kwargs={"digest_method": hashlib.sha256})
    cur = Serializer("k", fallback_signers=[{"digest_method": hashlib.sha256}])
    assert cur.needs_resign(old.dumps(7)) is True
    assert cur.needs_resign(cur.dumps(7)) is False


def test_tampered_or_unknown_key_rejected():  # AC4
    s = Serializer(["k1", "k2"])
    tok = s.dumps("x")
    bad = tok[:-1] + ("A" if tok[-1] != "A" else "B")
    with pytest.raises(BadSignature):
        s.needs_resign(bad)
    with pytest.raises(BadSignature):
        s.needs_resign(Serializer("stranger").dumps("x"))


def test_payload_never_deserialised():  # AC5
    s = Serializer(["k1", "k2"])
    garbage = s.make_signer().sign(b"\xff\xfe not json")  # bytes: str would be re-encoded as UTF-8
    with pytest.raises(BadPayload):
        s.loads(garbage)  # precondition: the payload really is undecodable
    assert s.needs_resign(garbage) is False
    old_garbage = Serializer(["k1"]).make_signer().sign(b"\xff\xfe not json")
    assert s.needs_resign(old_garbage) is True


def test_salt_is_honoured():  # AC6
    s = Serializer(["k1", "k2"])
    tok = s.dumps(1, salt="ctx")
    assert s.needs_resign(tok, salt="ctx") is False
    with pytest.raises(BadSignature):
        s.needs_resign(tok)
    with pytest.raises(BadSignature):
        s.needs_resign(tok, salt="other")
    old = Serializer(["k1"]).dumps(1, salt="ctx")
    assert s.needs_resign(old, salt="ctx") is True


def test_timed_serializer_ignores_age():  # AC7
    cur = TimedSerializer(["k1", "k2"])
    with freeze_time("2020-01-01"):
        old_tok = TimedSerializer(["k1"]).dumps(1)
        new_tok = cur.dumps(1)
    with freeze_time("2035-01-01"):
        assert cur.needs_resign(old_tok) is True
        assert cur.needs_resign(new_tok) is False


def test_str_bytes_idempotent_and_side_effect_free():  # AC8
    s = Serializer(["k1", "k2"])
    tok = Serializer(["k1"]).dumps([1, 2])
    keys_before = list(s.secret_keys)
    assert s.needs_resign(tok) is True
    assert s.needs_resign(tok.encode()) is True
    assert s.needs_resign(tok) is True
    assert s.secret_keys == keys_before
    assert s.loads(tok) == [1, 2]


@pytest.mark.parametrize("junk", ["", "no-signature-here", b"", "a.b.c"])
def test_garbage_input_is_bad_signature(junk):  # AC9
    with pytest.raises(BadSignature):
        Serializer(["k1", "k2"]).needs_resign(junk)
