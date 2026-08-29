# pyOpenSSL Authoring Provenance

## Source Freeze

- Upstream: `https://github.com/pyca/pyopenssl`
- Revision: `06dd9cba948b694e8de1e79ce3a458a7775e8af5`
- Commit: `Do not assume that ASN1_STRING is null terminated. (#1529)`
- Unprefixed archive SHA-256:
  `sha256:2ca6a8d913c3c717f4a4a644f7d6d12feba86906fa687c8dcfa7a069c1870385`
- License: Apache-2.0; `LICENSE` SHA-256:
  `sha256:cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- No submodules. The revision contains 56 tracked files and seven runtime/test
  Python files under `src/OpenSSL` and `tests`.

## Environment and Dependency Probe

- Authoring host: CPython 3.12.11, OpenSSL 3.5.7, Linux x86_64.
- Production base: `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`,
  `linux/amd64`.
- The candidate closure is an exact, hash-locked pip requirements artifact for
  `cryptography==50.0.0`, `cffi==2.1.1`, `pycparser==3.0`,
  `typing-extensions==4.16.0`, `setuptools==75.8.0`, and `wheel==0.45.1`.
- Native OpenSSL is consumed from the pinned image; no compiler or system
  library is fetched at evaluation time.

## Test Evidence

The upstream suite collected 432 items with isolated pytest collection. The
core `tests/test_crypto.py`, `tests/test_rand.py`, and `tests/test_util.py`
baseline collected 176 and passed 176 under CPython 3.12.11, pytest 8.3.5,
and the pinned cryptography line. Production uses 25 deterministic child-side
JSON scenarios because the remaining tests depend on live sockets, DTLS,
callbacks, host CA paths, current time, random bytes, and non-JSON CFFI
pointers. The final Harbor Oracle collected and passed 25/25 with reward 1.0;
stub and forgery controls collected 25/25 with reward 0.04, while bounded
install and call-hang controls returned reward 0.0.

## Security Boundary

The model Agent and verifier run with `no-network` and no static allowed hosts.
Only the trusted Oracle receives a run-scoped authorization for the exact
upstream host and verifies the full commit and archive digest before
materializing the reference. Hidden verifier code and cryptographic fixtures
are private CAS artifacts; reward files from the candidate are ignored.
