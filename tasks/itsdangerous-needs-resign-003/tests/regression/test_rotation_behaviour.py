"""Existing key-rotation behaviour that must hold in every state."""
import hashlib

import pytest

from itsdangerous import BadSignature, Serializer


def test_old_key_still_loads():
    old = Serializer(["k1"]).dumps({"a": 1})
    assert Serializer(["k1", "k2"]).loads(old) == {"a": 1}


def test_fallback_signer_still_loads():
    old = Serializer("k", signer_kwargs={"digest_method": hashlib.sha256}).dumps(5)
    assert Serializer("k", fallback_signers=[{"digest_method": hashlib.sha256}]).loads(old) == 5


def test_unknown_key_still_rejected_and_newest_signs():
    with pytest.raises(BadSignature):
        Serializer(["k1", "k2"]).loads(Serializer("zzz").dumps(1))
    s = Serializer(["k1", "k2"])
    assert Serializer(["k2"]).loads(s.dumps(1)) == 1
