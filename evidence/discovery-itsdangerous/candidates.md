# Feature candidates (python (EXPERIMENTAL))

Scanned 9 source files; 14 raw candidates; counts: {'tolerance-or-rule-parameter': 1, 'resource-limit-guard': 1, 'documented-todo': 1, 'untested-public-api': 5, 'option-threading': 6}

| id | kind | location | symbol | evidence |
|---|---|---|---|---|
| C001 | tolerance-or-rule-parameter | src/itsdangerous/timed.py:148 | TimestampSigner.unsign | `if age < 0:` |
| C002 | resource-limit-guard | src/itsdangerous/url_safe.py:46 | URLSafeSerializerMixin.load_payload | `json = zlib.decompress(json)` |
| C003 | option-threading | src/itsdangerous/serializer.py:285 | Serializer.make_signer | `return self.signer(self.secret_keys, salt=salt, **self.signer_kwargs)` |
| C004 | option-threading | src/itsdangerous/serializer.py:307 | Serializer.iter_unsigners | `yield fallback(secret_key, salt=salt, **kwargs)` |
| C005 | option-threading | src/itsdangerous/serializer.py:381 | Serializer._loads_unsafe_impl | `return True, self.loads(s, salt=salt, **load_kwargs)` |
| C006 | option-threading | src/itsdangerous/serializer.py:404 | Serializer.load_unsafe | `return self.loads_unsafe(f.read(), salt=salt)` |
| C007 | option-threading | src/itsdangerous/timed.py:164 | TimestampSigner.validate | `self.unsign(signed_value, max_age=max_age)` |
| C008 | documented-todo | src/itsdangerous/timed.py:182 | <comment> | `# TODO: Signature is incompatible because parameters were added` |
| C009 | untested-public-api | src/itsdangerous/serializer.py:33 | is_text_serializer | `def is_text_serializer` |
| C010 | untested-public-api | src/itsdangerous/serializer.py:271 | Serializer.dump_payload | `def dump_payload` |
| C011 | untested-public-api | src/itsdangerous/timed.py:29 | TimestampSigner.get_timestamp | `def get_timestamp` |
| C012 | untested-public-api | src/itsdangerous/timed.py:35 | TimestampSigner.timestamp_to_datetime | `def timestamp_to_datetime` |
| C013 | untested-public-api | src/itsdangerous/url_safe.py:55 | URLSafeSerializerMixin.dump_payload | `def dump_payload` |
