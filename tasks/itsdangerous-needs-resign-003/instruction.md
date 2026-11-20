# `Serializer.needs_resign`: detect tokens that should be re-issued after key rotation

## Context
`Serializer` accepts a list of `secret_keys` (oldest → newest; the newest signs) and optional `fallback_signers`
(other digest methods / signer classes) so old tokens keep verifying during a key or algorithm rotation.
Operators have no way to find out *which* valid tokens are still relying on an old key or fallback signer, so they
cannot tell when it is safe to retire it or when to silently re-issue a token.

## Requirement
Add `Serializer.needs_resign(s, salt=None) -> bool`.

1. If the signature verifies with the **current signer** (the newest secret key, the configured signer class and
   settings, and the given `salt`) → return `False`.
2. Otherwise, if it verifies with an **older key in `secret_keys`** or with any **fallback signer** (tried exactly as
   `loads` would try them, for the given `salt`) → return `True`.
3. If it verifies with none of them → raise `BadSignature` (the same exception `loads` raises).
4. Only the **signature** is examined: the payload is never deserialised (a validly signed token whose payload
   cannot be loaded still returns `True`/`False`), and for timestamp signers no age or timestamp check is made
   (an old token does not raise `SignatureExpired`).
5. `salt=None` means the serializer's configured salt; a different salt is a different signing context.
6. `s` may be `str` or `bytes`. The call has no side effects (the serializer's keys and configuration are unchanged).

## Acceptance criteria
| ID | Criterion |
|---|---|
| AC1 | token signed with the newest key → `False`. |
| AC2 | token signed with an older key in `secret_keys` → `True`; with three keys, middle and oldest → `True`, newest → `False`. |
| AC3 | token signed by a fallback signer only → `True`; a token from the current signer when fallbacks are configured → `False`. |
| AC4 | tampered token, or token signed with an unknown key → `BadSignature`. |
| AC5 | validly signed token with an undecodable payload → boolean result, no payload error. |
| AC6 | `salt` honoured: right salt → bool, wrong/missing salt → `BadSignature`. |
| AC7 | `TimedSerializer`: an expired-by-any-measure token returns a boolean, never `SignatureExpired`. |
| AC8 | accepts both `str` and `bytes` tokens; repeated calls give the same answer; `loads` of the same token is unaffected. |
| AC9 | empty or garbage input → `BadSignature`. |

## Non-goals / unspecified
URL-safe serializers' specific behaviour beyond inheritance; performance and timing side-channels; the exact message of
`BadSignature`; automatically re-signing the token.
