# Variation report

weighted Jaccard over files/symbols/entrypoints/criteria/test tokens (weights {'files': 0.2, 'symbols': 0.2, 'entrypoints': 0.2, 'criteria_tokens': 0.2, 'test_tokens': 0.2}); DISTINCT<0.25, REVIEW<0.5, else TOO_SIMILAR. Heuristic only: embeddings not used; every verdict needs manual adjudication.

## itsdangerous-leeway-001
- files: src/itsdangerous/timed.py
- symbols: TimedSerializer, TimestampSigner, validate
- feature tests: 12
- declared dimensions: time-based-validation, business-rule-tolerance, api-parameter-extension, input-validation
- summary: Clock-skew tolerance in timestamp verification: new keyword threaded through signer, validate and serializer; arithmetic rule on timestamps.

## itsdangerous-decompress-limit-002
- files: src/itsdangerous/url_safe.py
- symbols: URLSafeSerializerMixin, _decompress, max_decompressed_size
- feature tests: 7
- declared dimensions: resource-limits-security, streaming-decoding, error-handling, configuration-attribute
- summary: Bounded zlib decompression in URL-safe payload decoding: stateful streaming, memory bound, failure semantics on unsafe loads.

## itsdangerous-needs-resign-003
- files: src/itsdangerous/serializer.py
- symbols: Serializer, needs_resign
- feature tests: 9
- declared dimensions: key-rotation, signature-verification-state, new-public-method, fallback-compatibility
- summary: Operational key-rotation introspection: classify valid tokens by which signer verified them, without touching payload or timestamp.

## Pairwise

| A | B | composite | files | symbols | entrypoints | criteria | tests | verdict |
|---|---|---|---|---|---|---|---|---|
| itsdangerous-leeway-001 | itsdangerous-decompress-limit-002 | 0.061 | 0.0 | 0.0 | 0.08 | 0.086 | 0.14 | DISTINCT |
| itsdangerous-leeway-001 | itsdangerous-needs-resign-003 | 0.068 | 0.0 | 0.0 | 0.16 | 0.091 | 0.088 | DISTINCT |
| itsdangerous-decompress-limit-002 | itsdangerous-needs-resign-003 | 0.049 | 0.0 | 0.0 | 0.1 | 0.067 | 0.078 | DISTINCT |
