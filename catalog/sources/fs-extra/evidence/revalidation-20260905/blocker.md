# fs-extra instruction revalidation blocker

- Checked source content digest: `sha256:9acb6908c3940b637ef5bdd066da1a94f5c3e9ae0e471d50dee2876935ef7059`.
- All four declared private CAS artifacts were present and matched their declared size and SHA-256.
- Two production compiles completed with exit code 0 and were byte-identical (99 files; raw manifest `sha256:ba1d2bb9b3f07b6a60842c7d89feefa052e41741c12503aea0d8f510c8f1bdae`; canonical manifest `sha256:2ca7d8e664b2e3c1c98d4c8d7c7bb50e11e4cb357411d500aeeb70bbb1f66d4d`).
- The hash-valid Oracle bundle's `solve.sh` performs a runtime `git fetch` from `github.com` for revision `53a8d1a63c8eb30573110ed0f6528975f98801f0`.
- Because Agent, candidate, verifier, Oracle, and controls are required to run with NoNetwork, Harbor Oracle and controls were not started and no receipts were fabricated.
- Lifecycle, denominator, generated projection, and historical `production-evidence.json` remain unchanged.

Remediation: replace the Oracle payload with an offline, exact-revision source payload (or restore an approved offline CAS source artifact), then recompile and rerun the complete Oracle, empty, stub, forgery, and offline matrix.
