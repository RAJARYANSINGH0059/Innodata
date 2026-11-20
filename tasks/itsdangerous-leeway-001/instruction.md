# Clock-skew leeway for timestamp verification

## Context
`TimestampSigner.unsign(..., max_age=N)` rejects a signature whose timestamp is in the future
(`age < 0`) with `SignatureExpired`. When two services have slightly different clocks, a token signed
by one service can be rejected by another within the first few seconds of its life.

## Requirement
Add an optional keyword argument `leeway` (non-negative integer number of seconds, default `0`) so that
verifiers can tolerate a bounded amount of clock skew.

1. `TimestampSigner.unsign(signed_value, max_age=None, return_timestamp=False, leeway=0)`
   - Let `age = now - signed_timestamp`.
   - When `max_age` is given and `-leeway <= age < 0`, the signature is **accepted** (returns the value
     as before; `return_timestamp=True` still returns `(value, datetime)`).
   - When `max_age` is given and `age < -leeway`, raise `SignatureExpired` (with `payload` and
     `date_signed` set, as today).
   - `leeway` does **not** extend `max_age`: `age > max_age` still raises `SignatureExpired`.
   - `leeway=0` behaves exactly as before the change.
   - When `max_age` is `None`, behaviour is unchanged (no age checks); passing `leeway` is allowed.
   - A negative `leeway` raises `ValueError`.
   - Signature verification is unchanged: a tampered signature still raises `BadSignature`.
2. `TimestampSigner.validate(signed_value, max_age=None, leeway=0)` returns `True`/`False` consistent with (1).
3. `TimedSerializer.loads(s, max_age=None, return_timestamp=False, salt=None, leeway=0)` forwards
   `leeway` to the signer with the same semantics (including `return_timestamp`).

## Acceptance criteria
| ID | Criterion |
|---|---|
| AC1 | `max_age` set, `-leeway <= age < 0` → accepted (including the exact boundary `age == -leeway`). |
| AC2 | `max_age` set, `age < -leeway` → `SignatureExpired`. |
| AC3 | `leeway` never extends `max_age` (`age > max_age` → `SignatureExpired`). |
| AC4 | `leeway=0` (explicit) rejects any future-dated signature when `max_age` is set. |
| AC5 | Negative `leeway` → `ValueError`. |
| AC6 | `validate(..., leeway=)` mirrors `unsign`. |
| AC7 | `TimedSerializer.loads(..., leeway=)` forwards `leeway`, including with `return_timestamp=True`. |
| AC8 | Tampered signatures are still rejected when `leeway` is supplied. |
| AC9 | Without `max_age`, supplying `leeway` is accepted and changes nothing. |
| AC10 | Rejections beyond leeway carry `date_signed`. |
| AC11 | Default behaviour (no `leeway`) is unchanged. |

## Non-goals / unspecified
Behaviour for non-integer `leeway` (float, str, bool, None); `loads_unsafe`; URL-safe serializers; the exact
text of exception messages when `leeway > 0`; any change to `max_age` semantics.
