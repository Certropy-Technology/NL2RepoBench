# go-brotli instruction revalidation blocker

## Verified

- The expected migrated source digest is `sha256:1e4eb80c0f603305e7d2d2d0499df3729ceec7bdd8ea30f5d34c8c1b2e1e1048`.
- Go 1.26.5, Harbor 0.21.0, and all three declared private CAS objects passed exact size and SHA-256 checks.
- Two production compiles were run with `toolchain.go.lock.toml`, the parent CAS, `--allow-private`, and no `--allow-incomplete`. Both produced 75-file byte-identical bundles with raw manifest `sha256:afd00b6ee85a31a348b0869597c91508f29e9be0dbd1a470de6483f4cbeb9aea` and canonical digest `sha256:8ebab398f14f44563d0ce66d6147787f374e058229d9716e8a6c83ec7f2ee5cc`.
- Source validation, instruction quality, source-root network lint, JSON/TOML parsing, shell syntax, path/leak checks, and `git diff --check` passed. The exact source-root network lint reported zero `go-brotli` findings and zero errors.

## Blocker

The hash-valid Oracle bundle's `solve.sh` initializes a Git repository and runs `git fetch` against `github.com` for revision `6b8aef6ece266fa87b925ce3a913bc30dc4b7b70`. The task declares `reference_source_fetch = "forbidden"` and requires NoNetwork for Oracle and controls. Therefore Oracle, empty, stub, forgery, and offline Harbor runs were not started, and no new grading, network, collection, or reward receipt is claimed.

## Remediation

Replace the Oracle materializer with a locally supplied source archive that verifies both the frozen revision and archive digest, or register an equivalent private local payload. Then rerun the two-compilation check and the complete Harbor 0.21.0 Oracle/control matrix before changing lifecycle or production evidence. Historical evidence and lifecycle remain unchanged.
