# go-rosedb authoring provenance

## Source freeze

- Upstream: `https://github.com/rosedblabs/rosedb`
- Revision: `bcb43052ada686ec6d1345328e8299f502d3ef01`
- Commit date: `2026-02-09T14:34:41+08:00`
- Commit subject: `test: add comprehensive tests and fix btree iterator concurrency (#339)`
- Raw `git archive --format=tar` SHA-256:
  `41153fd1e40c1e7b18b90d46cfcf3a4bdc93fdc54c286823d2966b01686f527e`
- Tracked archive entries: 40; submodules: none.
- License: Apache-2.0; frozen `LICENSE` SHA-256:
  `a6cba85bc92e0cff7a450b1d873c0eaa2e9fc96bf472df0247a26bec77bf3ff9`.
- Frozen `go.mod` SHA-256:
  `62024f680827f330f87dea9328fa993bf3dc8a0b77b3fbeaf6f51fce1c7881b9`.
- Frozen `go.sum` SHA-256:
  `cb159ef0f850906386160273aee1d2fb44960b02a6fae696f2045e5a042d188c`.

The Oracle initializes an empty Git repository, fetches only the full frozen
SHA, asserts `FETCH_HEAD`, creates the same raw archive, and verifies its digest
before extracting it. Only the trusted Oracle run receives the exact source
host authorization.

## Environment and dependency closure

- Authoring Go: `go1.26.5-X:nodwarf5 linux/amd64`.
- Production Go base image:
  `docker.io/library/golang@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd`.
- Agent runtime image id:
  `sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f`.
- The frozen module closure contains normalized Go `1.26.5` metadata, the
  upstream `go.sum`, 404 vendor files, and `module.manifest.json` with every
  path and SHA-256. Vendor tree bytes total 7,305,496; aggregate sorted file
  digest: `761f69317abbc15fec7629fb3aac63dd98e660009bb95690b7f661287442d811`.
- The module closure was validated by the canonical
  `GoModulesPackageManager.validate_offline_store` and used with
  `GOPROXY=off`, `GOSUMDB=off`, `GOWORK=off`, and `GOTOOLCHAIN=local`.

## Upstream baseline and contract selection

The frozen source has 10 test files and 83 static `Test*` functions. After
materializing `vendor/`, `go test -count=1 ./...` passed offline: the root
package completed in 95.046 seconds, `index` in 0.009 seconds, `utils` in
0.012 seconds, and all example packages compiled. The root package exposes 64
public declarations according to `go doc -all`.

The Harbor task does not transplant upstream tests. Instead, one verifier-owned
leaf executes six bounded stateful scenarios through a task-specific typed JSON
bridge. This boundary keeps filesystem paths, callbacks, iterator objects,
watch channels, and wall-clock TTL state inside the unprivileged candidate
process while retaining explicit public-to-private traceability.

Auto-merge cron, raw record representation, internal index/WAL packages,
benchmarks, random helpers, and long concurrency stress are excluded because
they are not bounded serializable public behavior for this task version.

## Current production gate

- Source validation completed successfully on the current checkout.
- The catalog-wide network lint reported zero errors and no `go-rosedb`
  finding. Existing warnings belong to other catalog sources.
- Production compilation used `toolchain.go.lock.toml`, the task-local private
  artifact store, and `--allow-private`. The closed-world bundle contains 1,280
  files; its manifest SHA-256 is
  `17f07cc3ada85a263be5f2a79e3f15e307466dfb20850ce75523559187cc3b08`.
- Harbor 0.21.0 Oracle passed the frozen contract `1/1` with reward `1.0` and
  `public_network_available=false`.
- Empty and install-failure controls produced the allowed structured
  `candidate-installation-failed` `0/0` result. Stub, forgery, panic, hang,
  oversized-output, and background-process controls each collected the fixed
  denominator and scored `0/1`; all network probes were false. No residual
  `sleep 60` process remained after the background-process control.
- `tests/test_go_adapter.py` passed 9 tests and focused Ruff checks passed.

The first `prepare-control` attempt omitted `--toolchain` and exited 1 because
the CLI defaulted to the Python `toolchain.lock.toml`. Re-running every control
with the explicit production Go lock succeeded. This was a command
configuration error, not a task, candidate, verifier, or infrastructure
failure.
