"""Pre-existing behaviour that must hold in every state (AC11)."""
import pytest
from freezegun import freeze_time

from itsdangerous import SignatureExpired
from itsdangerous.timed import TimedSerializer, TimestampSigner


def _tok(sign_sec):
    s = TimestampSigner("secret")
    with freeze_time(f"2024-01-01 00:00:{sign_sec:02d}"):
        return s, s.sign(b"v")


def test_future_rejected_by_default_with_max_age():
    s, tok = _tok(31)
    with freeze_time("2024-01-01 00:00:30"):
        with pytest.raises(SignatureExpired):
            s.unsign(tok, max_age=60)


def test_expired_rejected_by_default():
    s, tok = _tok(0)
    with freeze_time("2024-01-01 00:00:30"):
        with pytest.raises(SignatureExpired):
            s.unsign(tok, max_age=10)
        assert s.unsign(tok, max_age=30) == b"v"


def test_future_accepted_without_max_age():
    s, tok = _tok(50)
    with freeze_time("2024-01-01 00:00:30"):
        assert s.unsign(tok) == b"v"


def test_validate_and_serializer_defaults():
    s, tok = _tok(31)
    ser = TimedSerializer("secret")
    with freeze_time("2024-01-01 00:00:31"):
        stok = ser.dumps([1])
    with freeze_time("2024-01-01 00:00:30"):
        assert s.validate(tok, max_age=60) is False
        with pytest.raises(SignatureExpired):
            ser.loads(stok, max_age=60)
    with freeze_time("2024-01-01 00:00:32"):
        assert ser.loads(stok, max_age=60) == [1]
