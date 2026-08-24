# `trimming` Blocked Conversion

Status: **blocked**. This directory is an audit record, not a publishable
Harbor task. No hidden test bytes or dataset entry are included.

## Evidence

- Legacy task: `test_files/trimming/`, declared test count `10`.
- Candidate upstream: `https://github.com/LucaCappelletti94/csv_trimming`.
- Candidate revision: `7ff2df6498037b927479e78d1bfe07dbc1ea5ab7`.
- License: MIT.
- Candidate `git archive` digest:
  `sha256:7bec56250445b8229d0426d4efdb2b09fc94d888125ad3345fe243184bf7693a`.
- Verifier image:
  `ghcr.io/multimodal-art-projection/nl2repobench/trimming@sha256:c92870271733eac4093fba9d6738056dc458ee443f073127234e09e69f053db4`.
- Platform: `linux/amd64`; image Python `3.10.18`.
- Static AST inspection found 10 tests, matching the legacy count.

The source layer matches the candidate revision, but eight retained setup/test
files in the verifier image do not match any blob across the upstream
repository's 58 commits. The image therefore contains an undocumented
behavioral/test overlay. The image config has no revision or owner-approved
overlay manifest.

## Decision

Do not generate a Harbor bundle or mark this task complete. Assigning the
overlay tests to the upstream revision would fabricate test provenance. To
reopen, obtain an owner-approved, licensed, versioned overlay artifact, then
run frozen collection, dependency closure, Oracle and controls.
