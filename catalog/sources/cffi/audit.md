# cffi authoring audit

## Frozen source

- Upstream: `https://github.com/python-cffi/cffi`
- Revision: `61fe449bd5bf9ae48211e822a7eefa5cb07c11d3`
- Exact `git archive --format=tar HEAD` source archive SHA-256: `sha256:3a426232fcb6ae371250e4e54428adb7b606ba77802bcf35025d059628082f0d`
- Source tree: `a2a978f86440242005ad936e5528d5ddbc0dbfd7`
- License: MIT-0; `LICENSE` SHA-256: `sha256:5ba24ddc57067f9249add644c3afc41a5d6dc37e23433ef759d95df370b0af63`

## Probe

The revision contains 39 Python test modules and a native `_cffi_backend`
extension linked against libffi. A digest-pinned Python 3.12.14 slim Bookworm
container with `build-essential`, `libffi-dev`, and `pkg-config` built the
source successfully. The representative `cffi1` FFI-object, argument, and new
FFI suites collected 168 tests and passed 164, with four expected skips. The
probe also observed only bounded callback warnings from upstream tests; no
network access was needed.

## Boundary decision

Native CData, callback, buffer, and local-library objects remain inside a
candidate UID 10001 subprocess. The custom verifier receives only JSON-safe
projections. Embedding, arbitrary dynamic libraries, platform matrix behavior,
and thread scheduling are excluded because no faithful deterministic child
adapter exists for them. This is a narrower public contract, not a claim of
full upstream test parity.

## Pending integration

The source descriptor references private hash-locked dependency, verifier, and
Oracle bundles. Parent integration must register those files in private CAS,
replace the placeholder refs, compile without `--allow-incomplete`, and rerun
Oracle plus all controls against the final manifest.
