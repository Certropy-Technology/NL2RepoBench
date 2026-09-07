# PyMongo instruction revalidation

## Result

Status: `infrastructure-pending`. The source digest was checked with
`validate-source` before any mutation. The declared Oracle, verifier, and
dependency artifacts were found locally and matched their exact declared
sizes and SHA-256 values. The embedded gzip source archive expands to the
declared frozen source digest for revision
`ebc4bffcc842464e48a3edbd04802d1a42bc818a`.

Two locked-toolchain production compiles completed successfully and produced
identical 62-file bundles and manifest digests. The generated bundle was
inspected for the declared task files and network policy; no replacement
proposal was made.

The fresh Harbor 0.21.0 Oracle attempt did not reach candidate or verifier
execution. Harbor raised `EnvironmentStartTimeoutError` while Docker was
building the agent environment after the 600-second startup bound. This is an
infrastructure result, not an Oracle score or a task/model failure. No Oracle,
control, reward, or network receipt is claimed from this attempt. See
`oracle-infrastructure.json` and the parent run artifact for the raw failure.

## Required follow-up

Retry once with the same source and final manifest in a clean Docker-capable
environment. If startup succeeds, run Oracle plus every supported control and
record fresh grading, network, and fixed-denominator receipts. Do not reuse
historical receipts from `production-evidence.json`.

## Validation

- `uv run nl2repo task validate-source catalog/sources/pymongo`: exit 0 before mutation and after evidence mutation.
- `uv run nl2repo task lint-network --tasks-root catalog/sources`: exit 0, error_count 0, no pymongo findings.
- Python verifier and shell controls: syntax checks passed.
- `git diff --check`: passed.
