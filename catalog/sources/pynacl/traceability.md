# PyNaCl Traceability

Frozen source: `pyca/pynacl` revision
`fddb5f3a012baa28d5ead6497ab2ae72c4221246`. The verifier has 49 unique
`pynacl/<scenario>` leaves. Candidate code is imported only in a UID 10001
child-side adapter; trusted code compares bounded JSON values.

| Public contract | Verifier leaves | Upstream authority |
| --- | --- | --- |
| Package metadata, `nacl.__all__`, typed marker | `metadata-imports` | `src/nacl/__init__.py`, `pyproject.toml` |
| Raw, hex, Base16/32/64, URL-safe encoding and failures | `encoding-*` | `src/nacl/encoding.py`, `tests/test_encoding.py` |
| Deterministic/random bytes and exception hierarchy | `utils-*`, `exceptions-*` | `src/nacl/utils.py`, `src/nacl/exceptions.py`, `tests/test_utils.py`, `tests/test_exc.py` |
| `SecretBox` construction, constants, combined/detached encryption, encoders, random nonce, authentication failures | `secretbox-*` | `src/nacl/secret.py`, `tests/test_secret.py` |
| `Aead` AAD behavior, encoders, random nonce, authentication failures | `aead-*` | `src/nacl/secret.py`, `tests/test_aead.py` |
| `PublicKey`, `PrivateKey`, deterministic seeds, encoders, equality, validation | `public-*` | `src/nacl/public.py`, `tests/test_public.py` |
| `Box` shared keys, decode, combined/detached ciphertext, errors | `box-*` | `src/nacl/public.py`, `tests/test_box.py` |
| Sealed-box randomized encryption, encoded roundtrip, public-only and tamper failures | `sealedbox-*` | `src/nacl/public.py`, `tests/test_sealed_box.py` |
| Signing/verify keys, combined and detached signatures, encoders, failures, Curve25519 conversion | `signing-*` | `src/nacl/signing.py`, `tests/test_signing.py` |
| SHA-256/512, BLAKE2b, SipHash and validation | `hash-*` | `src/nacl/hash.py`, `tests/test_hash.py`, `tests/test_shorthash.py` |
| Incremental BLAKE2b state, copy, digest stability, errors | `hashlib-*` | `src/nacl/hashlib.py`, `tests/test_generichash.py` |
| Argon2id constants, deterministic KDF, encoder, modular string verification, failures | `pwhash-*` | `src/nacl/pwhash/argon2id.py`, `src/nacl/pwhash/__init__.py`, `tests/test_pwhash.py` |
| Random key factories and bytes-subclass message shape | `generated-key-shapes`, `encrypted-message-bytes` | `tests/test_public.py`, `tests/test_signing.py`, `tests/test_secret.py` |

Reverse traceability is complete: every verifier leaf maps to one public
section above. Low-level `nacl.bindings` is excluded from the scored contract
because raw CFFI pointers and mutable native states do not cross the JSON
boundary safely; the high-level objects that consume those bindings remain
covered in the child process.
