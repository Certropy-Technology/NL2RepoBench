# go-badger instruction revalidation blocker

- The expected source digest `sha256:7143cc6ace710f6d42f9cdb23b8f75936ed7b2ff359bd13a218f7bc57b3591b0` was validated.
- The Oracle, module-bundle, and verifier CAS objects were present and verified by size and SHA-256.
- Two production compiles with `toolchain.go.lock.toml`, Harbor `0.21.0`, `--allow-private`, and no `--allow-incomplete` passed and were byte-identical: 2,017 files, manifest `sha256:a08b225f1cede3029d70f6aa180caf763a0d48d9bae25db95db47b8ab3fa1906`, canonical manifest `sha256:72315e45a147e88d34ad21f7f8f26b0fc4c754f75d58946c98214b03b8e8f981`.
- The Oracle payload verifies the fixed revision and archive digest, but performs a runtime GitHub fetch. The task policy forbids source-host authorization and all runtime network access.
- Oracle, empty, stub, forgery, and offline Harbor runs were therefore not started. No grading, reward, collection, or network receipt is claimed.
- Lifecycle, historical `production-evidence.json`, denominator, and generated projection were left unchanged.

Remediation: replace the runtime source acquisition with a trusted frozen source artifact that remains digest-bound and available without runtime network access, then recompile and rerun the complete Oracle/control matrix.
