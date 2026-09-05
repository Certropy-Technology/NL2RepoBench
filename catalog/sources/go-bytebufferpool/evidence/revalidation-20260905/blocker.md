# go-bytebufferpool revalidation blocker

The migrated catalog digest was verified as `sha256:836956c9153954e4cf20382d0a639a6a14e504e4251b319f446b72d560cb0da0`. All three private CAS objects were present and matched their declared size and SHA-256. Two production Go compiles using `toolchain.go.lock.toml`, `--allow-private`, and no `--allow-incomplete` produced byte-identical 67-file bundles.

The current Oracle bundle contains only `solve.sh`; it performs a runtime Git fetch from `github.com`. No source host was authorized. Local recovery checked the current bundle, task-local receipts, supervisor compile tree, authoring handoffs/worktrees, and the local Go module cache. The locally reconstructed 30,720-byte archive was `sha256:1f721918402f3304c012fbbfdee1d66a1e39e16352a78989302abc4f3d37b178`, which does not equal the frozen `sha256:a070768e029bc8a99e64611b6cf9905c193fe51b7a17044d3fb5b5fec7ca08cd`; it was rejected and no replacement bundle was proposed.

One strict NoNetwork Oracle run completed with Harbor exit code 0 but collected `0/1`, reward `0.0`, and `candidate-installation-failed`; the verifier reported that `go.mod` was absent because the forbidden fetch failed. Both network probes were false. Controls were not run because their Oracle source payload was unavailable. This is an artifact/verifier blocker, not a model result. Lifecycle, historical production evidence, and generated projection were left unchanged.

Durable details are in `artifact-check.json`, `compile-a-summary.json`, `compile-b-summary.json`, `oracle-inspection.json`, `oracle-result.json`, `oracle-grading.json`, `oracle-network.json`, `oracle-run-grading.json`, `oracle-run-network.json`, `oracle-fetch.log`, `oracle-verifier.log`, `failure-set.json`, and `matrix-status.json`.
