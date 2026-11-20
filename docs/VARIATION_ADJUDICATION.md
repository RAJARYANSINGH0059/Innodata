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
