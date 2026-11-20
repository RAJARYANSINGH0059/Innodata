# Manual adjudication — itsdangerous-leeway-001 vs itsdangerous-decompress-limit-002
Metric verdict: DISTINCT (composite 0.061). Manual reasoning (author's, not an independent human review):
| Dimension | 001 leeway | 002 decompress limit |
|---|---|---|
| Module / symbols | `timed.py`: TimestampSigner.unsign/validate, TimedSerializer.loads | `url_safe.py`: URLSafeSerializerMixin.load_payload/_decompress |
| Behaviour class | arithmetic rule on timestamps (clock-skew tolerance) | resource-bounded streaming decode (security) |
| Config surface | new keyword threaded through 3 call sites | class/instance attribute, no signature change |
| Failure semantics | SignatureExpired / ValueError | BadPayload; `loads_unsafe` → (False, None) |
| Oracle technique | time travel (freezegun), boundary arithmetic | memory bound (tracemalloc), size boundary, unsafe-load path |
Not shared: files, symbols, exceptions, test fixtures. Shared: repository, test framework, author. Conclusion: meaningfully different in behaviour and mechanism; NOT different in codebase.

## Task 003 (itsdangerous-needs-resign-003) vs 001 / 002
Metric: 0.068 / 0.049, DISTINCT. Manual reasoning (author's):
| Dimension | 003 needs_resign |
|---|---|
| Module / symbols | `serializer.py`: Serializer.needs_resign (reads iter_unsigners, secret_keys, fallback_signers) |
| Behaviour class | operational key-rotation introspection — a *classification* of valid tokens by which signer verified them (stateful config, no new failure mode) |
| API surface | new public method, no change to existing signatures or attributes |
| Failure semantics | BadSignature only; payload never decoded; timestamps ignored |
| Oracle technique | multi-key rotation matrices, fallback digests, garbage-payload precondition, side-effect check |
Not shared with 001/002: files, symbols, exceptions raised as the core behaviour. Shared: repository, author, freezegun/pytest style. Source of idea: discovery candidate C004 (heuristic hit, then human/AI design of the requirement).
