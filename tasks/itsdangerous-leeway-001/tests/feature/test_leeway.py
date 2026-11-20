"""Feature tests for the `leeway` requirement. Written from instruction.md only."""
import pytest
from freezegun import freeze_time

from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.timed import TimedSerializer, TimestampSigner

SIGN_AT = "2024-01-01 00:00:{:02d}"


def signed_with_age(age, secret="secret"):
    """Return a token that will have the requested age (seconds) when verified at 00:00:30."""
    s = TimestampSigner(secret)
    with freeze_time(SIGN_AT.format(30 - age)):
        return s, s.sign(b"payload")


def verify_at_30(fn):
    with freeze_time(SIGN_AT.format(30)):
        return fn()


@pytest.mark.parametrize("age", [-1, -3, -5])  # AC1 incl. boundary
def test_future_within_leeway_accepted(age):
    s, tok = signed_with_age(age)
    assert verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=5)) == b"payload"


@pytest.mark.parametrize("age", [-6, -20])  # AC2
def test_future_beyond_leeway_rejected(age):
    s, tok = signed_with_age(age)
    with pytest.raises(SignatureExpired):
        verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=5))


def test_leeway_does_not_extend_max_age():  # AC3
    s, tok = signed_with_age(11)
    with pytest.raises(SignatureExpired):
        verify_at_30(lambda: s.unsign(tok, max_age=10, leeway=100))
    s, tok = signed_with_age(10)
    assert verify_at_30(lambda: s.unsign(tok, max_age=10, leeway=100)) == b"payload"


def test_explicit_zero_leeway_rejects_future():  # AC4
    s, tok = signed_with_age(-1)
    with pytest.raises(SignatureExpired):
        verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=0))


@pytest.mark.parametrize("bad", [-1, -10])  # AC5
def test_negative_leeway_value_error(bad):
    s, tok = signed_with_age(0)
    with pytest.raises(ValueError):
        verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=bad))


def test_validate_mirrors_unsign():  # AC6
    s, tok = signed_with_age(-4)
    assert verify_at_30(lambda: s.validate(tok, max_age=60, leeway=5)) is True
    assert verify_at_30(lambda: s.validate(tok, max_age=60, leeway=3)) is False
    assert verify_at_30(lambda: s.validate(tok, max_age=60)) is False


def test_serializer_loads_forwards_leeway():  # AC7
    ser = TimedSerializer("secret")
    with freeze_time(SIGN_AT.format(34)):
        tok = ser.dumps({"a": 1})
    assert verify_at_30(lambda: ser.loads(tok, max_age=60, leeway=5)) == {"a": 1}
    value, ts = verify_at_30(lambda: ser.loads(tok, max_age=60, leeway=5, return_timestamp=True))
    assert value == {"a": 1} and ts.second == 34
    with pytest.raises(SignatureExpired):
        verify_at_30(lambda: ser.loads(tok, max_age=60, leeway=3))


def test_tampered_signature_still_rejected_with_leeway():  # AC8
    s, tok = signed_with_age(-2)
    bad = tok[:-1] + (b"A" if tok[-1:] != b"A" else b"B")
    with pytest.raises(BadSignature):
        verify_at_30(lambda: s.unsign(bad, max_age=60, leeway=5))


def test_leeway_without_max_age_is_harmless():  # AC9
    s, tok = signed_with_age(-25)  # far beyond leeway, but no max_age
    assert verify_at_30(lambda: s.unsign(tok, leeway=5)) == b"payload"


def test_rejection_carries_date_signed():  # AC10
    s, tok = signed_with_age(-9)
    with pytest.raises(SignatureExpired) as ei:
        verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=5))
    assert ei.value.date_signed is not None and ei.value.date_signed.second == 39
    assert ei.value.payload == b"payload"


def test_return_timestamp_with_leeway():  # AC1 + return_timestamp
    s, tok = signed_with_age(-2)
    value, ts = verify_at_30(lambda: s.unsign(tok, max_age=60, leeway=5, return_timestamp=True))
    assert value == b"payload" and ts.second == 32


def test_negative_leeway_rejected_even_without_max_age():  # AC5: unconditional ValueError
    s, tok = signed_with_age(0)
    with pytest.raises(ValueError):
        verify_at_30(lambda: s.unsign(tok, leeway=-1))
    with pytest.raises(ValueError):
        verify_at_30(lambda: s.validate(tok, leeway=-1))
