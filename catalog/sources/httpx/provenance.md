# HTTPX Remediation Evidence

The blocked HTTPX candidate was remediated to a deterministic offline
`MockTransport` slice rather than being rejected for having network APIs.

- Source revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- License: BSD-3-Clause
- Runtime: CPython 3.12.14, digest-pinned Debian/Python image
- Frozen private denominator: 24 JSON adapter leaves
- Private dependency bundle: referenced by `task.toml`, hash-locked wheels
- Private verifier bundle: referenced by `task.toml`, custom `custom-json-v1`
- Private Oracle bundle: referenced by `task.toml`
- Offline compiled smoke: `valid=true`, `collected=24`, `passed=24`, `reward=1.0`

The public catalog contains no source archive, hidden tests, verifier bytes or
wheelhouse. The full upstream network/httpbin/socket suite is not the frozen
denominator; the documented contract is the bounded mock transport slice.
Stub, forgery, timeout, review and pilot gates remain downstream.
