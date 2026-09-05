# Instruction revalidation blocker

- Task: `go-backoff`
- Expected catalog source digest: `sha256:3b1dc67d0ae75011132c29f9cd74f1a88532ee245de474be6bc3f33f22edb918`
- Source validation and instruction-quality validation passed.
- All three declared private CAS objects were present and SHA-256 verified.
- Two production compiles passed with identical 68-file trees and identical bundle manifest bytes.
- The Oracle artifact is not runnable under the required no-network policy: its `solve.sh` executes `git fetch` from `github.com` before materializing the reference workspace.
- Oracle and controls were therefore not run. The not-run summaries in this directory contain no fabricated grading, network, result, or reward values.
- Existing lifecycle, production evidence, denominator, generated projection, and public instruction were not changed.

## Remediation

Replace the Oracle payload with a private, hash-proven local source materializer, or provide a separately approved offline source archive that still asserts the frozen revision and archive digest. Then recompile from this source and rerun the complete Oracle/control matrix.
