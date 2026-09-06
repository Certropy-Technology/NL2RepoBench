# NoNetwork Oracle Revalidation Blocker: `locate-path`

## Scope

This record concerns only the instruction-migration revalidation on 2026-09-05.
It does not alter the existing lifecycle or production evidence, whose receipts
pre-date the migrated instruction and are therefore not current receipts.

The queue requires catalog source digest
`sha256:c0c6e3ac1f3c1f953890c90c985b54de44359bc9509c0dc6caaceccd21076cf9`.
Before creating this evidence, `validate-source` returned that exact digest,
task version `2.0.0`, and lifecycle status `controls-passed`.

## Artifact Verification

All four declared private artifacts exist in the parent CAS and their sizes and
SHA-256 values match `task.toml`. The compact result is
[`artifact-check.json`](artifact-check.json). This was not a missing-CAS
artifact failure.

## Oracle Inspection

The verified Oracle bundle is 20,480 bytes with SHA-256
`d813f5ac9a4cf9a15f2c84d9570eceb8e0d08e61112e8be610a505bd7e1ea9b1`.
Its members are `package-lock.json`, `runtime-package.json`, and `solve.sh`.
The script runs `git fetch` from `github.com` for revision
`4c4ee027b830c35ff7605421a8ad92208f1b868a`; it does not contain a source
archive or another installable reference payload.

The required frozen source archive is 30,720 bytes with SHA-256
`e5bf56cf0d89d2f6a1191cfea63f77157060ed42dcb3dcedc738de54595103bb`.
No source-host, package-registry, DNS, or other network authorization was used.

## Local Recovery

The local-recovery priority was followed before declaring this blocker:

1. The current Git object database does not contain the frozen revision.
2. All 30,720-byte regular files in the parent CAS and current locate-path
   source/projection were SHA-256 checked; none matched.
3. The generated Oracle projection was inspected and has no retained source
   payload.
4. Retained authoring sessions, handoffs, archives, historical worktrees, and
   local caches were searched by task ID, revision, digest, and bounded archive
   probes. No byte-identical archive was found.

The durable machine-readable search summary is
[`local-recovery-search.json`](local-recovery-search.json).

## Result And Next Step

Failure class: `artifact`.

The Oracle cannot be run under the required NoNetwork policy because its only
reference-source acquisition path is a network `git fetch` and no trusted local
source payload exists. No compile or Harbor run was attempted, and no Oracle or
control metrics are claimed for the migrated instruction.

Parent remediation is to recover or provide a byte-identical frozen source
archive, package it with a local-only Oracle `solve.sh`, register the new
private Oracle artifact in the shared CAS, update the artifact reference, then
double-compile and rerun Oracle plus the full control matrix. A replacement
bundle cannot be proposed from the bytes available in this worktree.
