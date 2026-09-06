# Leven NoNetwork Revalidation Blocker

The migrated instruction has source digest
`sha256:7c9f907259cdcee32e405ae5c5c67435d22bde3eabe9279c5033990982139d95`.
The previous manifest and Oracle/control receipts therefore cannot be reused.

All four declared private artifacts are present in the parent CAS and their
declared sizes and SHA-256 values match. The Oracle bundle itself is also
present, but contains only `solve.sh`. That script runs a GitHub `git fetch`
before it produces and checks the source archive, which violates this wave's
NoNetwork requirement for Oracle execution.

The required frozen archive is the 51,200-byte Git archive for revision
`fbc77137f0361b26aaa8465854e0ae8e492db6ba` with SHA-256
`14181e2e61abff5adcf7678a8a8e97cac49c90520d5f9d47e33a27687eeef055`.
The bounded trusted-local recovery search checked the current generated
runtime, task-local records, retained authoring and handoff archives, local
CAS, local caches, historical run receipts, and Docker resources. It found no
file with that exact digest. Historical receipts inventory an Oracle-produced
workspace, but that workspace has a rewritten `package.json` and generated
`package-lock.json`; it is not proof of the original frozen archive bytes.

No compile or Harbor run was started. Doing so would either use the stale
pre-migration receipts or run the Oracle's GitHub fetch. The source lifecycle
and production evidence are deliberately unchanged pending an exact local
payload.

## Remediation

Provide a trusted local source archive matching the required size and SHA-256,
or a parent-reviewed replacement Oracle bundle that embeds it. The parent must
register the replacement in CAS and update the artifact binding. Then compile
twice with the Node toolchain and rerun the Oracle, empty, stub, forgery, and
offline controls against the new manifest.
