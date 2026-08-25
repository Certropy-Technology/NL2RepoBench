# `autopep8` production authoring blocker

Status: **blocked**. This task-local record does not claim a production Harbor
runtime, Oracle pass, controls pass, review, pilot, commit, or publication.

## Frozen source

- Upstream: `https://github.com/hhatto/autopep8`
- Revision: `4046ad49e25b7fa1db275bf66b1b7d60600ac391`
- Version at the revision: `2.3.2`
- Commit date: `2025-01-14`
- Unprefixed `git archive --format=tar HEAD` SHA-256:
  `b0604345a9ac804f5eb6d30a0f779f61f64e679d651f43d16b2445b8ba799114`
- Submodules: none
- License: MIT. The pinned source's `LICENSE` is the standard MIT text.

The source freeze and license are not blockers.

## Dependency observation

The upstream project requires `pycodestyle >= 2.12.0` and uses setuptools as
its build backend. A bounded Python 3.12 linux/amd64 resolution selected:

- `pycodestyle==2.12.1`
- `setuptools==80.10.2`
- `wheel==0.45.1`

`uv pip compile --generate-hashes` produced a 564-byte requirements lock with
SHA-256
`c88b9902ab13f99c93d88155ed27836855f09f06f37ed8338b2d2b25e4fa5ef7`.
No wheel bytes were vendored. Under the task-only write restriction the lock
was not promoted into the shared private artifact store, so it is not an
authorized `lock_artifact` and cannot satisfy production compilation.

## Verifier blocker

The legacy runtime directly executes 564 effective upstream pytest cases in a
process that imports candidate code. That is not the required separate
subprocess verifier boundary and is removed rather than retained as a false
production runtime.

The intended replacement must freeze a bounded, meaningful public contract
covering core `fix_code` transformations, file formatting and mutation,
unified diff output, line-range confinement, aggressive levels, invalid
syntax, stdin, and CLI error/exit-code behavior. Every candidate import and
call must occur in an unprivileged subprocess against verifier-created
temporary files. No private verifier bundle, frozen JSON leaf denominator, or
Oracle bundle was completed in the bounded attempt, so no assertions were
weakened and no substitute denominator is declared.

## Strict gate result

The production compile was run once without `--allow-incomplete` and exited 1.
Its exact command, versions, output, and classification are recorded in
`evidence/production-compile.txt`. The compiler rejected the missing
hash-locked artifact, frozen test contract, private verifier inputs, command
artifact, and Oracle bundle before Docker execution. Therefore local Oracle
and controls were not authorized or run.

## Required next step

Promote the observed hash lock through the authorized private artifact flow,
author and freeze the bounded custom JSON subprocess verifier and local Oracle
bundle, then rerun strict compile followed by Harbor 0.21.0 Oracle, empty,
stub, forgery, and offline controls. Only successful, hash-bound receipts may
restore `catalog/tasks/autopep8` and transition the lifecycle to
`controls-passed`.
