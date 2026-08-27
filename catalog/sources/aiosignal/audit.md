# aiosignal authoring audit

## Frozen source

- Upstream: `https://github.com/aio-libs/aiosignal`
- Revision: `1c2bdc6dbd222463627638d2b46e9c3864e07597`
- Source archive: `git archive --format=tar HEAD`, SHA-256
  `sha256:3cce05c57a65da0028ebd03992845c571d9d5368524529acd422a77e9f283bde`
- License: Apache-2.0, `LICENSE` SHA-256
  `sha256:6fd5243e92dd7f98ec69c7ac377728e74905709ff527a5bf98d6d0263c04f5b6`
- Package version: `1.4.0`; runtime API is `aiosignal.Signal`.

## Inventory and probes

- Source tree contains one runtime module and one upstream test module.
- Upstream collection with `pytest -c /dev/null --collect-only -q tests`: 13 tests.
- Upstream behavior with `pytest -c /dev/null -o asyncio_mode=auto -q tests`: 13 passed.
- The original pytest configuration preloads coverage and contains an option that
  is incompatible with the selected plugin configuration; the verifier uses an
  isolated JSON scenario runner instead of inheriting that configuration.
- Candidate install probe with `pip install --no-deps --target ... source`: exit 0.
- Private verifier adapter smoke: 13 scenarios passed against the frozen source.

## Runtime and dependency closure

- Runtime: CPython 3.12.14 on `python:3.12.14-slim-bookworm`.
- Base image digest: `sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`.
- Hash lock: `provenance/requirements.lock.txt`, 23607 bytes,
  `sha256:4d1de95a0e21f5796f116eaa9dcf415bdb831e8daac34d42d955f8eeb7c93d31`.
- Candidate and verifier dependencies are build-time installed; Agent and verifier
  runtime policy is `no-network` with no static allowed hosts.

## Harbor preparation

- Production compile command: `uv run nl2repo harbor compile catalog/sources/aiosignal --output .nl2repo/compiled --toolchain toolchain.lock.toml --artifact-root .nl2repo/artifacts --allow-private`, exit 0.
- Bundle manifest: `.nl2repo/compiled/aiosignal/bundle.manifest.json`, 57 files,
  0 integrity errors, SHA-256
  `sha256:b5ff27b420b07fe5600883dccd43a0bd10dd6ff8091fb4614ea711255643ec14`;
  canonical manifest digest is
  `sha256:3b6de9b940ebec2b9ffac96e1140e521029cbd44d3d21e45cc32292e9a5ecf00`.
- Verifier bundle CAS ref: `sha256:6decbbda752e19fd1319e62280baf20c37b992c74ff8ff876223e4bff0ed8b71`, 20480 bytes.
- Oracle bundle CAS ref: `sha256:99c67b3b14645de6820b12ae620535504fd7a4c29d9cfb8227c26081e4b68148`, 10240 bytes.
- Prepared controls: `.nl2repo/controls/aiosignal/aiosignal-stub` and
  `.nl2repo/controls/aiosignal/aiosignal-forgery`.
- `uv run nl2repo task lint-network --tasks-root catalog/sources` exit 0 with
  0 errors; the command reports pre-existing warnings for other catalog tasks.

## Deferred gates

Harbor Oracle, empty, stub, forgery, timeout, and offline runs were not executed
because this authoring lane is prohibited from starting a Harbor Agent Run. The
handoff therefore does not claim Oracle reward, control reward, or production
validity; the separate run loop must execute and record those receipts.
