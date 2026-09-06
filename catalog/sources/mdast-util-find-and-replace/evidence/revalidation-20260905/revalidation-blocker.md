# Instruction revalidation blocker

The queue requires source digest
`sha256:722aaea920d6bc96b8cd1ae17321909fef2592acc6bdbd075120e8318f373736`.
`uv run nl2repo task validate-source catalog/sources/mdast-util-find-and-replace`
returned that exact digest before this evidence was added.

The four declared private artifacts are present in the parent CAS and match
their declared sizes and SHA-256 values. The Oracle artifact is also hash-valid,
but its complete inner inventory contains only declarations, package metadata,
and `solve.sh`; it has no frozen source archive. The exact artifact and Oracle
inspection are recorded in `artifact-check.json` and `oracle-inspection.json`.

The Oracle `solve.sh` fetches
`https://github.com/syntax-tree/mdast-util-find-and-replace` at revision
`fd73ef856ab4f7b6326e3255aea36f439b75e2d5`, creates a Git archive, and checks
for archive digest
`sha256:be821926713dee556bca6f0aa2cff873a8fef69d142f438327e84f08cf2d57d9`.
That runtime source fetch violates this revalidation's NoNetwork contract.
No source-host authorization was added and no Harbor run was started.

A bounded offline recovery search covered the generated projection, task-local
files, retained task-specific authoring records and paths, private CAS, and
local package/module cache material. No exact archive or Git object proving both
the frozen revision and archive digest was found, so no replacement bundle was
created. Search details are in `local-recovery-search.json`.

The existing `task.toml`, lifecycle state, and historical
`production-evidence.json` remain unchanged. This evidence records a
revalidation artifact/verifier blocker and does not claim fresh Oracle or
control receipts. The next unblock action is to recover the exact frozen source
archive from a trusted local backup or Git object store, construct an offline
Oracle bundle, then have the parent register it, compile twice, and rerun the
complete Oracle and supported control matrix.
