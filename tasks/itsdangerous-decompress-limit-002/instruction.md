# Decompression-size limit for URL-safe serializers

## Context
`URLSafeSerializer` / `URLSafeTimedSerializer` zlib-compress large payloads (marked by a leading `.`).
`load_payload` decompresses without any bound, so a small attacker-supplied token can expand to hundreds of
megabytes (a "zip bomb"). This matters most for `loads_unsafe`, which decodes the payload of a token whose
signature is **invalid**.

## Requirement
Add a class attribute `max_decompressed_size: int | None = None` to `URLSafeSerializerMixin` (and therefore to
`URLSafeSerializer` and `URLSafeTimedSerializer`). It may be overridden on a subclass or set on an instance.

1. `None` (default): behaviour is exactly as before (no limit).
2. An integer `N >= 0` and a **compressed** payload: if the decompressed data would be larger than `N` bytes,
   `load_payload` raises `BadPayload`. A decompressed size of exactly `N` bytes is accepted.
3. The check must be enforced **while decompressing**: the implementation must not first materialise the full
   decompressed output. Peak additional Python memory during a rejected load must stay within a small constant
   of the limit (not proportional to the bomb's real size).
4. Uncompressed payloads (no leading `.`) are not affected by the limit.
5. Consequences for existing entry points (no new signatures):
   - `loads(...)` of a validly signed oversized token raises `BadPayload`.
   - `loads_unsafe(...)` of an oversized token with an invalid signature returns `(False, None)`.
6. Corrupt compressed data still raises `BadPayload` (unchanged), with or without a limit.

## Acceptance criteria
| ID | Criterion |
|---|---|
| AC1 | limit set, decompressed size `> N` → `BadPayload` (`URLSafeSerializer`, `URLSafeTimedSerializer`). |
| AC2 | decompressed size `== N` accepted; `N+1`-byte payload with limit `N` rejected. |
| AC3 | default `None`: no limit, existing large payloads load. |
| AC4 | Rejection happens without full materialisation (peak memory bound, tracemalloc). |
| AC5 | Uncompressed payloads load regardless of limit. |
| AC6 | `loads_unsafe` on an oversized token with an invalid signature returns `(False, None)`. |
| AC7 | Limit can be set on an instance and via subclass attribute; instances are independent. |
| AC8 | Corrupt zlib data → `BadPayload`, with and without a limit. |

## Non-goals / unspecified
Negative or non-integer limits; limits for uncompressed data; the exact `BadPayload` message; changes to
`dump_payload`; the plain `Serializer`.
