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

## Pairwise

| A | B | composite | files | symbols | entrypoints | criteria | tests | verdict |
|---|---|---|---|---|---|---|---|---|
| itsdangerous-leeway-001 | itsdangerous-decompress-limit-002 | 0.061 | 0.0 | 0.0 | 0.08 | 0.086 | 0.14 | DISTINCT |
